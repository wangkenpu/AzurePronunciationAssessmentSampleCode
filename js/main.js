var sdk = require("microsoft-cognitiveservices-speech-sdk");
const _ = require('lodash');
var fs = require("fs");


function main () {
    const subscriptionKey = "YourSubscriptionKey";
    const serviceRegion = "YourServiceRegion";
    const audioFile = "../resources/Lauren_audio.wav";
    const topicFile = "../resources/Lauren_topic.txt";

    var topic = fs.readFileSync(topicFile, "utf8");
    var audioConfig = sdk.AudioConfig.fromWavFileInput(fs.readFileSync(audioFile));
    var speechConfig = sdk.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);

    // setting the recognition language to English.
    speechConfig.speechRecognitionLanguage = "en-US";

    // create the speech recognizer.
    var reco = new sdk.SpeechRecognizer(speechConfig, audioConfig);
    const connection = sdk.Connection.fromRecognizer(reco);
    const phraseDetectionConfig = `{
        "enrichment": {
            "pronunciationAssessment": {
                "referenceText": "",
                "gradingSystem": "HundredMark",
                "granularity": "Word",
                "dimension": "Comprehensive",
                "EnableMiscue": "False"
            },
            "contentAssessment": {
                "topic": "${topic}"
            }
        }
    }`;
    connection.setMessageProperty("speech.context", "phraseDetection", JSON.parse(phraseDetectionConfig));

    const phraseOutputConfig = `{
        "format": "Detailed",
        "detailed": {
            "options": [
                "WordTimings",
                "PronunciationAssessment",
                "ContentAssessment",
                "SNR"
            ]
        }
    }`;
    connection.setMessageProperty("speech.context", "phraseOutput", JSON.parse(phraseOutputConfig));
    connection.close();

    var results = [];
    var recognizedText = "";

    reco.recognized = function (s, e) {
        jo = JSON.parse(e.result.properties.getProperty(sdk.PropertyId.SpeechServiceResponse_JsonResult));
        if (jo.DisplayText != ".") {
            console.log(`Recognizing: ${jo.DisplayText}`);
            recognizedText += jo.DisplayText;
        }
        results.push(jo);
    }

    function onRecognizedResult() {
        console.log(`Recognized text: ${recognizedText}`);
        var contentAssessmentResult = results[results.length-1]["NBest"][0]["ContentAssessment"];
        console.log("Content assessment result: ", contentAssessmentResult);
    }

    reco.canceled = function (s, e) {
        if (e.reason === sdk.CancellationReason.Error) {
            var str = "(cancel) Reason: " + sdk.CancellationReason[e.reason] + ": " + e.errorDetails;
            console.log(str);
        }
        reco.stopContinuousRecognitionAsync();
    };

    reco.sessionStopped = function (s, e) {
        reco.stopContinuousRecognitionAsync();
        reco.close();
        onRecognizedResult();
    };

    reco.startContinuousRecognitionAsync();
}


main()
