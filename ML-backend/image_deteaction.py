import json
from ultralytics import YOLO


model = YOLO("./best.pt")

def img_detection(imgName):
  main= []
  results = model.predict("uploads/" + imgName,vid_stride=10)
  for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()  # display to screen
    result.save(filename="result.jpg")
    print(result)
    res = result.to_json()
    data = json.loads(res)
    classes = [item["class"] for item in data]
    for element in classes:
      if element not in main:
          main.append(element)

  # Convert back to a list
  main_array = list(main)

  OnlyPills = [18]
  OnlyInj=[3]
  pillsAndInj = [18,3]
  pillsAndSyrup = [18,21]
  humanAndPills =[18,17]
  humanAndSmoke = [17,20]

  if set(main_array) == set(OnlyPills):
    print("Only Pills")
    response ={
        "isFlagged": True,
        "tag": "Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if set(main_array) == set(OnlyInj):
    print("Only Injection")
    response ={
        "isFlagged": True,
        "tag":"Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if set(main_array) == set(pillsAndInj):
    print("Pills & Injections")
    response ={
        "isFlagged": True,
        "tag": "Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if set(main_array) == set(pillsAndSyrup):
    print("Pills & Syrup")
    response ={
        "isFlagged": True,
        "tag": "Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if set(main_array) == set(humanAndPills):
    print("Pills & Human")
    response ={
        "isFlagged": True,
        "tag": "Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if set(main_array) == set(humanAndSmoke):
    print("Pills & Smoke")
    response ={
        "isFlagged": True,
        "tag": "Yellow",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

  if not main_array:
   response = {
        "isFlagged": False,
        "tag": "Green",
         "classes": []
         
        }
   res = json.dumps(response)
   return res

  else:
    response ={
        "isFlagged": True,
        "tag": "Red",
       "classes": main_array,
    }
    res = json.dumps(response)
    return res

__all__ =["img_detection"]