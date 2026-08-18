"""Set Allego recording config. The radiens client cannot do this: ConfigRecording has a
required `recordingType` enum that radiens.api.api_allego.set_recording_config never sets,
so the message fails to serialize with 'Exception serializing request!'. Build it directly.
"""
import grpc, radiens.utils.interceptors as itc
from radiens.allego_client import AllegoClient
from radiens.grpc_radiens import allegoserver_pb2 as ap, allegoserver_pb2_grpc as ag

from core import paths as PATHS
DEST = str(PATHS.RAW_ROOT)

c = AllegoClient(); c.get_status()
chan = grpc.intercept_channel(
    grpc.insecure_channel("127.0.0.1:50051"),
    itc.MetadataClientInterceptor(id_token=itc.SessionMetaData._instance._id_token))
stub = ag.AllegoCoreStub(chan)

req = ap.ConfigRecording(
    baseFileName="allego",
    baseFilePath=DEST,
    dataSourceIdx=0,
    timeStamp=True,
    splitFilesByPort=False,
    forceStartAtTStamp0=False,
    recordingType=ap.continuous,
)
stub.SetConfigRecording(req, timeout=60)
s = c.get_status()
print("record cfg now:", s.recording)
