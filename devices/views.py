# Create your views here.
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt 
from devices import models_Camera
from devices import models_XPS
from devices.forms import AngleScan
from models_LiquidHandler import Serial_Delution

 
import Image, cStringIO
import numpy
from django.template import Context, loader
c=models_Camera.Camera()
xps=models_XPS.Sample()


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
    

    
def getSampleRotationStageLocation(request):
         return HttpResponse({(xps.getPosition()):'position'})
@csrf_exempt  
def anglescan(request):
    print 'Great Success HUGH  '
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

    s=Serial_Delution(float(request.REQUEST['max_conc']),float(request.REQUEST['min_conc']),float(request.REQUEST['sample_count']))
    s.getConcentrationSamples()
    s.getConcentrationArray()
    s.getSampleVolumeArray()
    s.final()
    return HttpResponse()
    
    
    

    
    