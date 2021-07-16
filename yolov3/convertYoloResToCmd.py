import json
import numpy as np

def FaceRec():
    pass

def process(resfromYolo, current_color, last):
    amplify = 100
    
    c_value = 0.92         # Stop threashold
    turn_factor = 0.008
    c_factor = 0.05
    step = 4
    
    size = '320x240'
    img_w, img_h = tuple([int(p) for p in size.split('x')])
    
    res = {}
    if not len(resfromYolo):
        res['TR'] = 1 * amplify
        return json.dumps(res), False
    
    det_color = [det[0] for det in resfromYolo]
    if current_color not in det_color:
        res['TR'] = 1 * amplify
        return json.dumps(res), False
    
    else:
        ref = [index for index in range(len(det_color)) if det_color[index] == current_color]
        for index in ref:
            index = det_color.index(current_color)
            label, xywh = resfromYolo[index]
            x, y, w, h = xywh[0], xywh[1], xywh[2], xywh[3]
        
            offset = x - img_w / 2
            if (h > c_value * img_h) & (abs(offset) < c_factor * img_w):
                res['MF'] = 300
                print('Pillar Found!')
                return json.dumps(res), True
        
            else:
                c = round(c_factor - 0.02 * (h / img_h), 3)
                c = 0.03
                if abs(offset) > c * img_w:
                    if offset > 0:
                        #res['TL'] = int(amplify * offset * t_factor / (w / img_w))
                        res['TR'] = int(amplify * offset * turn_factor)
                    else:
                        #res['TR'] = int(amplify * abs(offset) * t_factor / (w / img_w))
                        res['TL'] = int(amplify * abs(offset) * turn_factor)
                else:
                    res['MF'] = int(step * amplify / np.exp(2 * (h / img_h - 0.75)))
                
                return json.dumps(res), False

def FinalDrop(resfromYolo, last):
    current_color = 'white'
    
    amplify = 100
    
    c_value = 0.3         # Stop threashold
    turn_factor = 0.008
    c_factor = 0.05
    step = 4
    
    size = '320x240'
    img_w, img_h = tuple([int(p) for p in size.split('x')])
    
    res = {}
    if not len(resfromYolo):
        res['TR'] = 1 * amplify
        return json.dumps(res), False
    
    det_color = [det[0] for det in resfromYolo]
    if current_color not in det_color:
        res['TR'] = 1 * amplify
        return json.dumps(res), False
    
    else:
        ref = [index for index in range(len(det_color)) if det_color[index] == current_color]
        for index in ref:
            index = det_color.index(current_color)
            label, xywh = resfromYolo[index]
            x, y, w, h = xywh[0], xywh[1], xywh[2], xywh[3]
        
            offset = x - img_w / 2
            if (h > c_value * img_h) & (abs(offset) < c_factor * img_w):
                res['MF'] = 1000
                res['ACT'] = 2
                return json.dumps(res), True
        
            else:
                c = round(c_factor - 0.02 * (h / img_h), 3)
                if abs(offset) > c * img_w:
                    if offset > 0:
                        #res['TL'] = int(amplify * offset * t_factor / (w / img_w))
                        res['TR'] = int(amplify * offset * turn_factor)
                    else:
                        #res['TR'] = int(amplify * abs(offset) * t_factor / (w / img_w))
                        res['TL'] = int(amplify * abs(offset) * turn_factor)
                else:
                    res['MF'] = int(step * amplify / np.exp(2 * (h / img_h - 0.8)))
                
                return json.dumps(res), False