﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using speechsdk = Microsoft.CognitiveServices.Speech;
using Newtonsoft.Json;
using System.IO;

namespace Samples
{
    class Program
    {
        static void Main(string[] args)
        {
            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..");
            string topic_path = Path.Combine(basePath, "resources", "Lauren_topic.txt");
            string wav_path = Path.Combine(basePath, "resources", "Lauren_audio.wav");
            string language = "en-US";
            string topic = File.ReadAllText(topic_path);
            if (File.Exists(topic_path))
            {
                Console.WriteLine("True");
                string resultJson = Task.Run(() => PronunciationAssessmentContent(wav_path, language, topic)).GetAwaiter().GetResult();
                Console.WriteLine(resultJson);
            }

        }


        public static async Task<string> PronunciationAssessmentContent(string wavePath, string language = "en-US", string topic = "")
        {
            var speechSubscriptionKey = "YourSubscriptionKey";
            var speechRegion = "YourServiceRegion";

            //var speechConfig = speechsdk.SpeechConfig.FromSubscription("HOST", "SUBSCRIPTION");
            var speechConfig = speechsdk.SpeechConfig.FromSubscription(speechSubscriptionKey, speechRegion);
            var audioConfig = speechsdk.Audio.AudioConfig.FromWavFileInput(wavePath);
            var speechRecognizer = new speechsdk.SpeechRecognizer(speechConfig, language.Replace("_", "-"), audioConfig);

            // speechRecognizer.SessionStarted += (s, e) => Console.WriteLine($"WaveName: {wavePath}, Session ID: {e.SessionId}");
            var connection = speechsdk.Connection.FromRecognizer(speechRecognizer);

            var phraseDetectionConfig = new
            {
                enrichment = new
                {
                    pronunciationAssessment = new
                    {
                        referenceText = "",
                        gradingSystem = "HundredMark",
                        granularity = "Word",
                        dimension = "Comprehensive",
                        enableMiscue = "False"
                    },
                    contentAssessment = new
                    {
                        topic = topic
                    }
                }
            };
            connection.SetMessageProperty("speech.context", "phraseDetection", JsonConvert.SerializeObject(phraseDetectionConfig));

            var phraseOutputConfig = new
            {
                format = "Detailed",
                detailed = new
                {
                    options = new[]
                    {
                    "WordTimings",
                    "PronunciationAssessment",
                    "ContentAssessment",
                    "SNR"
                }
                }
            };
            connection.SetMessageProperty("speech.context", "phraseOutput", JsonConvert.SerializeObject(phraseOutputConfig));

            // open the connection
            connection.Open(forContinuousRecognition: false);

            try
            {
                // apply the pronunciation assessment configuration to the speech recognizer
                var result = await speechRecognizer.RecognizeOnceAsync();
                if (result.Reason == speechsdk.ResultReason.RecognizedSpeech)
                {
                    var pronunciationResultJson = result.Properties.GetProperty(speechsdk.PropertyId.SpeechServiceResponse_JsonResult);
                    return pronunciationResultJson;
                }
                else
                {
                    var message = $">>> [ERROR] WaveName: {wavePath}, Reason: {result.Reason}";
                    throw new Exception(message);
                }
            }
            finally
            {
                // close the connection
                connection.Close();
            }
        }
    }
}
