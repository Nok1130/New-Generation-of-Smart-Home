import boto3
import cv2
import time
import sys

# Initialize Rekognition client
rekognition_client = boto3.client('rekognition', aws_access_key_id='',
                           aws_secret_access_key='', region_name='')

# Function to analyze emotions
def analyze_emotions(image_bytes):
    response = rekognition_client.detect_faces(
        Image={
            'Bytes': image_bytes
        },
        Attributes=['ALL']
    )
    return response['FaceDetails']

def main(update_emotion):
    # Capture frames from video
    cap = cv2.VideoCapture(0) 

    if not cap.isOpened():
        print("Error: Camera could not be accessed.")

    print("Camera successfully accessed!")
    time.sleep(2)

    count = 0
    previous_emotion = ""
    global current_emotion

    while(True):
        ret, frame = cap.read()
        
        # show photo
        cv2.imshow('frame', frame)
        
        _, image_bytes = cv2.imencode('.jpg', frame)
        image_bytes = image_bytes.tobytes()

        # Analyze emotions
        face_details = analyze_emotions(image_bytes)
        for face in face_details:
            emotions = face['Emotions']

            if emotions:  # Check if the list is not empty 
                current_emotion = emotions[0]['Type']  
                print(current_emotion)
                if current_emotion == previous_emotion:
                    count += 1
                else:
                    count = 0
                    previous_emotion = current_emotion
                
                if count == 3:
                    # print("you are " + current_emotion)
                    update_emotion(current_emotion)
                    cap.release()
                    cv2.destroyAllWindows()
                    return 
                    sys.exit()
                
        # press q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
        # if stop == "True":
            break

    cap.release()
    cv2.destroyAllWindows()
    
if __name__=="__main__":
    print(main())