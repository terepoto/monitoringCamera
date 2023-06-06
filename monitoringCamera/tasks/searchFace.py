import boto3
import cv2
import datetime
from botocore.exceptions import ClientError
from django.conf import settings
from models.models import Faces
from models.models import Position_History
from apscheduler.schedulers.background import BackgroundScheduler


def get_face_from_camera():
    print('システム実行')
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cascade = cv2.CascadeClassifier("./haarcascades/haarcascade_frontalface_default.xml")

    lists = cascade.detectMultiScale(img_gray, 1.1)

    for key, (x, y, w, h) in enumerate(lists):
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), thickness=2)
        file_name = str(datetime.datetime.timestamp(datetime.datetime.now())) + 'k' + str(key) + ".jpg"
        cv2.imwrite(file_name, frame[y - 20:y + h + 20, x - 20:x + w + 20])
        upload_face(file_name, settings.S3_BUCKET, file_name)
        search_face(file_name)

    cap.release()
    cv2.destroyAllWindows()


def upload_face(file_name, bucket, object_name=None):
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True


def search_face(face_image):
    bucket = settings.S3_BUCKET
    collection_id = settings.AMAZON_REKOGNITION_COLLECTION
    file_name = face_image
    threshold = 70
    max_faces = 2

    client = boto3.client('rekognition')

    response = client.search_faces_by_image(CollectionId=collection_id,
                                            Image={'S3Object': {'Bucket': bucket, 'Name': file_name}},
                                            FaceMatchThreshold=threshold,
                                            MaxFaces=max_faces)

    face_matches = response['FaceMatches']
    print('Matching faces')
    print(len(face_matches))
    for match in face_matches:
        print('FaceId:' + match['Face']['FaceId'])
        print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
        Position_History(face_id=match['Face']['FaceId'], camera_id=0, position_x=0 , position_y=0).save()

    if len(face_matches) == 0:
        add_faces_to_collection(bucket, file_name, collection_id)


def add_faces_to_collection(bucket, photo, collection_id):
    client = boto3.client('rekognition')

    response = client.index_faces(CollectionId=collection_id,
                                  Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                  ExternalImageId=photo,
                                  MaxFaces=1,
                                  QualityFilter="AUTO",
                                  DetectionAttributes=['ALL'])

    print('Results for ' + photo)
    print('Faces indexed:')
    for faceRecord in response['FaceRecords']:
        print('  Face ID: ' + faceRecord['Face']['FaceId'])
        print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
        Faces(rekognition_face_id=faceRecord['Face']['FaceId'], face_img=photo).save()

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_face_from_camera, 'interval', seconds=10)
    scheduler.start()
