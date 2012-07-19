# Create your views here.
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt 
from devices import models_Camera
from devices import models_XPS
from devices import models_Polarization_Experiment
from devices.forms import AngleScan



import Image, cStringIO
import numpy
import json
from django.template import Context, loader
#c=models_Camera.Camera()
xps=models_XPS.Sample()
seriaDilutionInstance=0
pe=models_Polarization_Experiment.PolazrizationExperiment()



def index(request):
    c=models_Camera.Camera()
    img=numpy.asarray(c.getImage())
    
    image = Image.fromarray(numpy.uint8(img))
    response = HttpResponse(mimetype="image/png")
    image.save(response, "PNG")
    return response
    #img.save
    #return HttpResponse("You're looking at poll %s." % img )
    #file_out = cStringIO.StringIO()
    #im.save(file_out, format)

    #file_out.reset()

    #print "Content-Type: image/jpeg\n"
    #print file_out.read()

    #file_out.close()
    #file.close()
    #return HttpResponse("You're looking at poll %s." % )

@never_cache
def getcamera(request):

    t = loader.get_template('results.html')
    c = Context({})
    return HttpResponse(t.render(c))

@never_cache
def getImage(request):
 
    img=numpy.asarray(c.getImage())
    
    image = Image.fromarray(numpy.uint8(img))
    response = HttpResponse(mimetype="image/png")
    image.save(response, "PNG")
    return response

def getSampleRotationWidget(request):
    t = loader.get_template('rotation-sample.html')
    xps_data = {
            'max_velocity': xps.getMaxVelocity(),
            'curr_position': xps.getPosition()
       
        }
    c = Context({'xps_data':xps_data})
    return HttpResponse(t.render(c))

def getInputPolarizationWidget(request):
    t = loader.get_template('PolarizationWidget.html')
    xps_data = {
            'stage_name':'Input Polarization Stage',
            'max_velocity': xps.getMaxVelocity(),
            'curr_position': xps.getPosition()
        }
    c = Context({'xps_data':xps_data})
    return HttpResponse(t.render(c))
    
def getOutputPolarizationWidget(request):
    t = loader.get_template('PolarizationWidget.html')
    xps_data = {
            'stage_name':'Output Polarization Stage',
            'max_velocity': xps.getMaxVelocity(),
            'curr_position': xps.getPosition()
        }
    c = Context({'xps_data':xps_data})
    return HttpResponse(t.render(c))

def getPolarizationExperiment(request):
    t = loader.get_template('GetPolarizationExperiment.html')
    xps_data = {
            'stage_name':'Output Polarization Stage',
            'max_velocity': xps.getMaxVelocity(),
            'curr_position': xps.getPosition()
        }
    c = Context({'xps_data':xps_data})
    return HttpResponse(t.render(c))
    
@csrf_exempt    
def polScan(request):

    input_pol_start = int(request.REQUEST['input_pol_start'])
    input_pol_end = int(request.REQUEST['input_pol_end'])
    input_pol_step = int(request.REQUEST['input_pol_step'])
    output_pol_start = int(request.REQUEST['output_pol_start'])
    output_pol_end = int(request.REQUEST['output_pol_end'])
    output_pol_step = int(request.REQUEST['output_pol_step'])
    

    arr= pe.scan(input_pol_start,input_pol_end,input_pol_step,output_pol_start,output_pol_end,output_pol_step)

    #return HttpResponse({(arr):'arr'})
    return HttpResponse (json.dumps(arr), mimetype="application/json")
@csrf_exempt     
def stopPolScan(request):
    pe.stopScan()
    return HttpResponse()

    
    
    

def getSampleRotationStageLocation(request):
         return HttpResponse({(xps.getPosition()):'position'})
@csrf_exempt  
def anglescan(request):

    sample_rotation_start=0
    sample_rotation_end=12
    sample_rotation_velocity=34

    if request.method == 'POST':
        sample_rotation_start = int(request.REQUEST['sample_rotation_start'])
        sample_rotation_end = int(request.REQUEST['sample_rotation_end'])
        sample_rotation_velocity = int(request.REQUEST['sample_rotation_velocity'])
        print type(sample_rotation_start)
        print sample_rotation_end
        print sample_rotation_velocity
    xps.angle_scan(sample_rotation_start,sample_rotation_end,sample_rotation_velocity)
    return HttpResponse({round(xps.getPosition()):'position'})
@csrf_exempt     
def movesamplestage (request):
    print request.REQUEST['move_sample_stage']
    xps.moveTo(int(request.REQUEST['move_sample_stage']))
    return HttpResponse({(xps.getPosition()):'position'})
    getSampleRotationStageLocation(request)
    
    
def getSerialDilutionWidget (request):
    t = loader.get_template('LiquidHandler.html')
    c = Context()
    return HttpResponse(t.render(c))
    
@csrf_exempt
def serialDilution(request):

    from models_LiquidHandler import *
    max_conc=float(request.REQUEST['max_conc'])
    min_conc=float(request.REQUEST['min_conc'])
    sample_count=float(request.REQUEST['sample_count'])
    
    print "Max Conc "+ str(max_conc)
    print "Min Conc "+ str(min_conc)
    global seriaDilutionInstance
    seriaDilutionInstance=Serial_Delution(max_conc,min_conc,sample_count)
    return HttpResponse()
    
@csrf_exempt     
def serialDilutionPrepareSample(request):

    print str(type(serialDilution))
    seriaDilutionInstance.prepareSample()
    return HttpResponse()
    
    
    

    
    