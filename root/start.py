import os
import sys
import re
from scripts import load_fixtures, create_fixtures, create_rnd_scale
from subprocess import call
from eyevacs.models import Experiment, External_Source_Data, External_Choice_Task, External_Order_Scale, External_Baseline_Choice_Task

#paths
root = '' #sys.path[0]
external_data_path = './external_data/'
fixture_output = './eyevacs/fixtures/'
output_data_path = './eyevacs/'
experiment_name = ''
exp_filename = ''
current_exp_id = None
use_def_scales = True
default_scales = [('Max',1,6),('Regret',1,5),('Involvement',1,4),('SearchGoals',1,4),('Happiness',1,4)]



def SetExperimentDjangoPK():
    '''Gets a free personal key identifier for the new current Experiment Model.'''

    exp_count = Experiment.objects.count()
    return exp_count + 1

def MakeExperiment(name, language):
    '''Create an Experiment Model Fixture.'''

    single_model = r'{"model":"%s","pk":%s,"fields":{%s}}'
    output = "[%s]"
    existing_experiments = Experiment.objects.all()
    #OVERWRITE or new experiment?
    #djangoPK = None
    global current_exp_id
    if len(existing_experiments) > 0:
        for current_exp in existing_experiments:
            ascii_name = re.sub("[u']","",current_exp.name) #regular expression!
            if ascii_name == name:
                print name , ' already exists!'
                print 'ID and Fixture will override an existing Experiment! (No changes to database.)'

                current_exp_id = current_exp.pk
                break
            else:
                #print '### NO NAME MATCH ###'
                current_exp_id = SetExperimentDjangoPK() #django get unused experiment ID, counts existing exeriments + 1
    else:
        current_exp_id = 1
    #djangoLANGUAGE = 'de' #has to be dynamic, will be gotten by admin form or by manual overwrite in the internal django admin app
    experiment_fields = r'"name":"%s","language":"%s"'
    experiment = ('eyevacs.Experiment', current_exp_id, experiment_fields % (name, language))
    global exp_filename
    exp_filename = 'EXP_' + name + '_' +language + '_' + str(current_exp_id) + '_FIX.json'
    full_path = fixture_output + exp_filename
    f = open (full_path, 'w')
    experiment_output = output % single_model % experiment
    f.write(experiment_output)
    f.close()

def LoadExpFixture(exp_json_filename):
#    relative_path = 
    try:
        print '\n*** Importing external fixtures ***: \n'
        #print sys.executable, root,'\\manage.py loaddata', exp_json_filename
        #execfile('./manage.py loaddata ' + exp_json_filename)
        call([sys.executable, 'manage.py', 'loaddata', exp_json_filename])
        print '-- Imported ' + exp_json_filename +' sucessfully --'
    except:
        print '############### ERROR importing experiment...'
        print exp_json_filename

def InitPaths():
    #global vars
    global root
    global external_data_path
    global fixture_output
    global output_data_path

    #root path
    temp_root = sys.path[0]
    #regular expression substitution
    root = re.sub(r"\\","/",temp_root)
    external_data_path = './external_data/'
    fixture_output = './eyevacs/fixtures/' + experiment_name + '/'
    #Experiment fixture folder
    if not os.path.isdir(fixture_output):
        os.makedirs(fixture_output)
    #rnd data folder
    rnd_data_fullpath = './eyevacs/data/' + experiment_name + '/'
    if not os.path.isdir(rnd_data_fullpath):
        os.makedirs(rnd_data_fullpath)
    global output_data_path
    output_data_path = rnd_data_fullpath

def CreateDefaultRndScales():
    for i in range(0,len(default_scales),1):
        print default_scales[i]
        create_rnd_scale.main(current_exp_id, default_scales[i])

def CheckLang():
        lang_choices = ("de","en")
        choice = raw_input('Enter Language: "de" or "en": \n -->')
        if choice not in lang_choices:
            CheckLang()
        else:
            return choice
def Echo():
    print 'Database Content:'
    print '-----------------'
    print 'Experiment Count: ', Experiment.objects.count()
    print 'Ext Src Data Count: ', External_Source_Data.objects.count()
    print 'Ext ChoiceTask Count: ', External_Choice_Task.objects.count()
    print 'Ext BaselineCT Count: ', External_Baseline_Choice_Task.objects.count()
    print 'Random Order Count: ', External_Order_Scale.objects.count()
    print ''

def FlushAll():
    Echo()
    sure = raw_input('FLUSHING ALL DJANGO MODEL OBJECTS!!!\n --- Are you sure? --- \n type "yes" to to DELETE!\n --- every other key to abort. ---')
    if sure == 'yes':
        Experiment.objects.all().delete()
        External_Source_Data.objects.all().delete()
        External_Choice_Task.objects.all().delete()
        External_Baseline_Choice_Task.objects.all().delete()
        External_Order_Scale.objects.all().delete()
        print '\n ### Objects have been deleted ###!\n'
    else:
        print '\n ### Deletion ABORTED ###! \n'
    Echo()

def main():

    print '********************'
    print '*Script starting...*'
    print '********************'
    print ''
    #Experiment
    #Create Fixture, input: name and language
    global experiment_name
    global fixture_output
    #DEBUG switches, do the work in CHUNCKS: dont load at first! (last switch)
    switch_new_exp= 0
    switch_ct = 0
    switch_default_rnd = 0
    switch_rnd = 0 #overridden by default rnd
    switch_load_fixtures = 0

    if switch_new_exp:
        #NEW EXPERIMENT
        exps = Experiment.objects.all()
        print 'EXISTING EXPERIMENTS:'
        print '---------------------'
        for e in exps:
            print e.name
        experiment_name = raw_input('\nEnter Name of EXPERIMENT: \n #####:')
        experiment_language = CheckLang()
    else:
        #LAST IMPORTED EXPERIMENT
        exp_count = Experiment.objects.count()
        curr_exp = Experiment.objects.get(pk=exp_count)
        #experiment_name = 'OXIQUATL'
        experiment_name = curr_exp.name
        experiment_language = curr_exp.language

    InitPaths()
    MakeExperiment(experiment_name, experiment_language)
    LoadExpFixture(fixture_output+ exp_filename)
    print ' ### CURRENT EXP ID:', current_exp_id
    if switch_ct:
        create_fixtures.main(current_exp_id, external_data_path, fixture_output)
    if switch_rnd:
        create_rnd_scale.main(current_exp_id)
    if switch_default_rnd:
        CreateDefaultRndScales()
    if switch_load_fixtures:
        print root
        load_fixtures.Run('.'+root, fixture_output[1:], output_data_path[1:])

    Echo()

    print '\n___________________________'
    print 'Everthing went as expected!'


main()

#if __name__ == "__main__":
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djVacs.settings")
    #from django.core.management import execute_from_command_line
    #execute_from_command_line(sys.argv)
    #__main__()

#execfile('./start.py')
