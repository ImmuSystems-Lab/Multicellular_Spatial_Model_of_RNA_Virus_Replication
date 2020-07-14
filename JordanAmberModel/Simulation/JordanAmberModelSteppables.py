from cc3d.core.PySteppables import *
import numpy as np

plot_ODEModel = True
plot_CellModel = True
feedback_IFNModel = True

min_to_mcs = 10.0  # min/mcs
hours_to_mcs = min_to_mcs / 60.0 # hours/mcs
days_to_mcs = min_to_mcs / 1440.0  # day/mcs
days_to_simulate = 10.0  # 10 in the original model

# Modified code to make IFNe production dependent on the number of infected cells (P)
IFNModel_string = '''
    //Equations
    E2a: -> IFN         ; P*(k11*RIGI*V+k12*(V^n)/(k13+(V^n))+k14*IRF7P)    ;
    E2b: IFN -> IFNe    ; k21*IFN                                           ;
    E3a: IFNe ->        ; t2*IFNe                                           ;
    E4a: -> STATP       ; P*k31*IFNe/(k32+k33*IFNe)                         ;
    E4b: STATP ->       ; t3*STATP                                          ;
    E5a: -> IRF7        ; P*(k41*STATP+k42*IRF7P)                           ;
    E5b: IRF7 ->        ; t4*IRF7                                           ;
    E6a: -> IRF7P       ; P*k51*IRF7                                        ;
    E6b: IRF7P ->       ; t5*IRF7P                                          ;
    E7a: P ->           ; P*k61*V                                           ;
    E8a: -> V           ; P*(k71*V)/(1.0+k72*IFN*7E-5)                      ;
    E8b: V ->           ; k73*V                                             ;

    //Parameters
    k11 = 0.0       ; 
    k12 = 9.746     ; 
    k13 = 12.511    ; 
    k14 = 13.562    ;
    k21 = 10.385    ;
    t2  = 3.481     ;
    k31 = 45.922    ;
    k32 = 5.464     ;
    k33 = 0.068     ;
    t3  = 0.3       ;
    k41 = 0.115     ;
    k42 = 1.053     ;
    t4  = 0.75      ;
    k51 = 0.202     ;
    t5  = 0.3       ;
    k61 = 0.635     ;
    k71 = 1.537     ;
    k72 = 47.883    ;
    k73 = 0.197     ;
    n   = 3.0       ;

    //Initial Conditions
    P    = 1.0      ;
    RIGI = 1.0      ;
    IRF7 = 0.0      ;
    V    = 6.9e-8   ;
'''

# Viral Replication Model
viral_model_string = '''
    E7a: P ->           ; P*k61*V                    ;
    E8a: -> V           ; P*k71*V/(1.0+k72*IFN*7E-5) ;
    E8b: V ->           ; k73*V                      ;

    //Parameters
    k61 = 0.635     ;
    k71 = 1.537     ;
    k72 = 47.883    ;
    k73 = 0.197     ;

    //Initial Conditions
    P    =  1.0     ;
    V    =  6.9e-8  ; 
    
    //Inputs
    IFN  =  0.0     ;
'''

# Modified code to make IFNe production dependent on the number of infected cells (P)
IFN_model_string = '''
    //Equations
    E2a: -> IFN         ; P*(k12*(V^n)/(k13+(V^n))+k14*IRF7P)               ;
    E2b: IFN ->         ; k21*IFN                                           ;
    E4a: -> STATP       ; P*k31*IFNe/(k32+k33*IFNe)                         ;
    E4b: STATP ->       ; t3*STATP                                          ;
    E5a: -> IRF7        ; P*(k41*STATP+k42*IRF7P)                           ;
    E5b: IRF7 ->        ; t4*IRF7                                           ;
    E6a: -> IRF7P       ; P*k51*IRF7                                        ;
    E6b: IRF7P ->       ; t5*IRF7P                                          ;

    //Parameters
    k12 = 9.746     ; 
    k13 = 12.511    ; 
    k14 = 13.562    ;
    k21 = 10.385    ;
    t2  = 3.481     ;
    k31 = 45.922    ;
    k32 = 5.464     ;
    k33 = 0.068     ;
    t3  = 0.3       ;
    k41 = 0.115     ;
    k42 = 1.053     ;
    t4  = 0.75      ;
    k51 = 0.202     ;
    t5  = 0.3       ;
    n   = 3.0       ;

    // Inputs
    P    = 0.0      ;
    V    = 0.0      ;
    IFNe = 0.0      ;
'''

class ODEModelSteppable(SteppableBasePy):
    def __init__(self, frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        # Uptading max simulation steps using scaling factor to simulate 10 days
        self.get_xml_element('simulation_steps').cdata = days_to_simulate / days_to_mcs

        self.add_free_floating_antimony(model_string=IFNModel_string, model_name='IFNModel',
                                        step_size=hours_to_mcs)

        self.add_antimony_to_cell_types(model_string=viral_model_string, model_name='VModel',
                                        cell_types=[self.I2], step_size=hours_to_mcs)

        self.add_antimony_to_cell_types(model_string=IFN_model_string, model_name='IModel',
                                        cell_types=[self.I2], step_size=hours_to_mcs)

    def step(self, mcs):
        self.timestep_sbml()

class CellularModelSteppable(SteppableBasePy):
    def __init__(self, frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        # set initial model parameters
        self.initial_infected = len(self.cell_list_by_type(self.I2))
        self.ExtracellularIFN = 0.0
        self.get_xml_element('IFNe_decay').cdata = self.sbml.IFNModel['k73'] * hours_to_mcs

    def step(self, mcs):
        secretorIFN = self.get_field_secretor("IFNe")
        # P to D transition - Jordan Model
        # E7a: P -> ; P * k61 * V;
        for cell in self.cell_list_by_type(self.I2):
            k61 = cell.sbml.VModel['k61'] * hours_to_mcs
            V = cell.sbml.VModel['V']
            P = cell.sbml.VModel['P']
            p_I2toD = k61 * V * (1-P)
            if np.random.random() < p_I2toD:
                cell.type = self.DEAD

        ## Updating values of intracellular models
        for cell in self.cell_list_by_type(self.I2):
            if not feedback_IFNModel:
                ## Inputs to the INF model
                cell.sbml.IModel['V'] = self.sbml.IFNModel['V']
                cell.sbml.IModel['P'] = self.sbml.IFNModel['P']
                cell.sbml.IModel['IFNe'] = self.sbml.IFNModel['IFNe']
                ## Inputs to the Virus model
                cell.sbml.VModel['IFN'] = self.sbml.IFNModel['IFN']
            if feedback_IFNModel:
                cell.sbml.IModel['V'] = cell.sbml.VModel['V']
                cell.sbml.IModel['P'] = cell.sbml.VModel['P']
                IFNe = secretorIFN.amountSeenByCell(cell)
                cell.sbml.IModel['IFNe'] = IFNe
                ## Inputs to the Virus model
                cell.sbml.VModel['IFN'] = cell.sbml.IModel['IFN']

        ## Production of extracellular IFN - Jordan Model
        # E2b: IFN -> IFNe; k21 * IFN ;
        I = self.ExtracellularIFN
        k21 = self.sbml.IFNModel['k21'] * hours_to_mcs
        for cell in self.cell_list_by_type(self.I2):
            intracellularIFN = cell.sbml.IModel['IFN']
            p = k21 * intracellularIFN
            release = secretorIFN.secreteInsideCellTotalCount(cell, p / cell.volume)
            self.ExtracellularIFN += release.tot_amount
        # E3a: IFNe -> ; t2*IFNe ;
        t2 = self.sbml.IFNModel['t2'] * hours_to_mcs
        self.ExtracellularIFN -= t2 * I

        ## Measure amount of extracellular IFN field
        self.ExtracellularIFN_Field = 0
        for cell in self.cell_list_by_type(self.I2):
            I = secretorIFN.amountSeenByCell(cell)
            self.ExtracellularIFN_Field += I

        # Dictonary to pass information between steppables
        self.shared_steppable_vars['ExtracellularIFN'] = self.ExtracellularIFN
        self.shared_steppable_vars['ExtracellularIFN_Field'] = self.ExtracellularIFN_Field

class IFNPlotSteppable(SteppableBasePy):
    def __init__(self, frequency=1):
        SteppableBasePy.__init__(self, frequency)

    def start(self):
        self.initial_infected = len(self.cell_list_by_type(self.I2))
        # Initialize Graphic Window for Jordan IFN model
        if (plot_ODEModel == True) or (plot_CellModel == True):
            self.plot_win1 = self.add_new_plot_window(title='V',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win2 = self.add_new_plot_window(title='H',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win3 = self.add_new_plot_window(title='P',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win4 = self.add_new_plot_window(title='IFNe',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win5 = self.add_new_plot_window(title='STATP',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win6 = self.add_new_plot_window(title='IRF7',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win7 = self.add_new_plot_window(title='IRF7P',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            self.plot_win8 = self.add_new_plot_window(title='INF',
                                                      x_axis_title='Hours',
                                                      y_axis_title='Variable', x_scale_type='linear',
                                                      y_scale_type='linear',
                                                      grid=False, config_options={'legend': True})

            if plot_ODEModel:
                self.plot_win1.add_plot("ODEV", style='Dots', color='yellow', size=5)
                self.plot_win2.add_plot("ODEH", style='Dots', color='white', size=5)
                self.plot_win3.add_plot("ODEP", style='Dots', color='red', size=5)
                self.plot_win4.add_plot("ODEIFNe", style='Dots', color='orange', size=5)
                self.plot_win5.add_plot("ODESTATP", style='Dots', color='blue', size=5)
                self.plot_win6.add_plot("ODEIRF7", style='Dots', color='green', size=5)
                self.plot_win7.add_plot("ODEIRF7P", style='Dots', color='purple', size=5)
                self.plot_win8.add_plot("ODEIFN", style='Dots', color='magenta', size=5)

            if plot_CellModel:
                self.plot_win1.add_plot("CC3DV", style='Lines', color='yellow', size=5)
                self.plot_win2.add_plot("CC3DH", style='Lines', color='white', size=5)
                self.plot_win3.add_plot("CC3DP", style='Lines', color='red', size=5)
                self.plot_win4.add_plot("CC3DIFNe", style='Lines', color='orange', size=5)
                self.plot_win4.add_plot("CC3DIFNe2", style='Lines', color='yellow', size=5)
                self.plot_win5.add_plot("CC3DSTATP", style='Lines', color='blue', size=5)
                self.plot_win6.add_plot("CC3DIRF7", style='Lines', color='green', size=5)
                self.plot_win7.add_plot("CC3DIRF7P", style='Lines', color='purple', size=5)
                self.plot_win8.add_plot("CC3DIFN", style='Lines', color='magenta', size=5)

    def step(self, mcs):
        if plot_ODEModel:
            L = len(self.cell_list_by_type(self.I2))
            self.plot_win1.add_data_point("ODEV", mcs * hours_to_mcs, self.sbml.IFNModel['V'])
            self.plot_win2.add_data_point("ODEH", mcs * hours_to_mcs, self.sbml.IFNModel['P'])
            self.plot_win3.add_data_point("ODEP", mcs * hours_to_mcs, self.sbml.IFNModel['P'])
            self.plot_win4.add_data_point("ODEIFNe", mcs * hours_to_mcs, self.sbml.IFNModel['IFNe']*L)
            self.plot_win5.add_data_point("ODESTATP", mcs * hours_to_mcs, self.sbml.IFNModel['STATP'])
            self.plot_win6.add_data_point("ODEIRF7", mcs * hours_to_mcs, self.sbml.IFNModel['IRF7'])
            self.plot_win7.add_data_point("ODEIRF7P", mcs * hours_to_mcs, self.sbml.IFNModel['IRF7P'])
            self.plot_win8.add_data_point("ODEINF", mcs * hours_to_mcs, self.sbml.IFNModel['IFN'])

        if plot_CellModel:
            L = len(self.cell_list_by_type(self.I2))
            avgV = 0.0
            avgH = 0.0
            avgSTATP = 0.0
            avgIRF7 = 0.0
            avgIRF7P = 0.0
            avgIFN = 0.0

            for cell in self.cell_list_by_type(self.I2):
                avgV += cell.sbml.VModel['V'] / L
                avgH += cell.sbml.VModel['P'] / L
                avgSTATP += cell.sbml.IModel['STATP'] / L
                avgIRF7 += cell.sbml.IModel['IRF7'] / L
                avgIRF7P += cell.sbml.IModel['IRF7P'] / L
                avgIFN += cell.sbml.IModel['IRF7P'] / L

            self.plot_win1.add_data_point("CC3DV", mcs * hours_to_mcs, avgV)
            self.plot_win2.add_data_point("CC3DH", mcs * hours_to_mcs, avgH)
            self.plot_win3.add_data_point("CC3DP", mcs * hours_to_mcs, L / self.initial_infected)
            self.plot_win4.add_data_point("CC3DIFNe", mcs * hours_to_mcs,
                                          self.shared_steppable_vars['ExtracellularIFN'])
            self.plot_win4.add_data_point("CC3DIFNe2", mcs * hours_to_mcs,
                                          self.shared_steppable_vars['ExtracellularIFN_Field'])
            self.plot_win5.add_data_point("CC3DSTATP", mcs * hours_to_mcs, avgSTATP)
            self.plot_win6.add_data_point("CC3DIRF7", mcs * hours_to_mcs, avgIRF7)
            self.plot_win7.add_data_point("CC3DIRF7P", mcs * hours_to_mcs, avgIRF7P)
            self.plot_win8.add_data_point("CC3DIFN", mcs * hours_to_mcs, avgIFN)