using System;
using System.IO;
using System.Threading.Tasks;
using Newtonsoft.Json;

using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.CognitiveServices.Speech.PronunciationAssessment;


namespace Samples
{
    class Program
    {
        private static readonly string choose = " Please choose one of the following samples:";
        private static readonly string mainPrompt = " Your choice (or 0 to exit): ";
        private static readonly string exiting = "\n Exiting...";
        private static readonly string invalid = "\n Invalid input, choose again.";
        private static readonly string done = "\n Done!";
        static void Main(string[] args)
        {

            ConsoleKeyInfo x;

            do
            {
                Console.WriteLine("");
                Console.WriteLine(" Pronunciation Assessment examples");
                Console.WriteLine("");
                Console.WriteLine(choose);
                Console.WriteLine("");
                Console.WriteLine(" 1. Pronunciation Assessment with Content.");
                Console.WriteLine(" 2. Pronunciation Assessment with Prosody.");
                Console.WriteLine("");
                Console.Write(mainPrompt);

                x = Console.ReadKey();
                Console.WriteLine("");
                bool sampleWasRun = true;

                switch (x.Key)
                {
                    case ConsoleKey.D1:
                    case ConsoleKey.NumPad1:
                        GetContentResult().Wait();
                        break;
                    case ConsoleKey.D2:
                    case ConsoleKey.NumPad2:
                        GetProsodyResult().Wait();
                        break;
                    case ConsoleKey.D0:
                    case ConsoleKey.NumPad0:
                        Console.WriteLine(exiting);
                        sampleWasRun = false;
                        break;
                    default:
                        Console.WriteLine(invalid);
                        sampleWasRun = false;
                        break;
                }

                if (sampleWasRun) Console.WriteLine(done);

            } while (x.Key != ConsoleKey.D0);

        }

        // Pronunciation assessment configured with json
        // See more information at https://aka.ms/csspeech/pa
        public static async Task GetProsodyResult()
        {
            // Creates an instance of a speech config with specified subscription key and service region.
            // Replace with your own subscription key and service region (e.g., "westus").
            var config = SpeechConfig.FromSubscription("YourSubscriptionKey", "YourServiceRegion");

            // Replace the language with your language in BCP-47 format, e.g., en-US.
            var language = "en-US";

            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..", "..", "..");
            string scriptPath = Path.Combine(basePath, "resources", "weather_script.txt");
            string wavePath = Path.Combine(basePath, "resources", "weather_audio.wav");
            string referenceText = File.ReadAllText(scriptPath);

            string scenario_id = "[scenario ID will be assigned by product team]";

            // Creates an instance of audio config from an audio file
            var audioConfig = AudioConfig.FromWavFileInput(wavePath);

            // create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
            string json_config = "{\"GradingSystem\":\"HundredMark\",\"Granularity\":\"Phoneme\",\"EnableMiscue\":true, \"ScenarioId\":\""+scenario_id+"\"}";
            var pronunciationConfig = PronunciationAssessmentConfig.FromJson(json_config);
            pronunciationConfig.ReferenceText = referenceText;

            // Creates a speech recognizer for the specified language
            using (var recognizer = new SpeechRecognizer(config, language, audioConfig))
            {
                // Starts recognizing.
                pronunciationConfig.ApplyTo(recognizer);

                // Starts speech recognition, and returns after a single utterance is recognized.
                // For long-running multi-utterance recognition, use StartContinuousRecognitionAsync() instead.
                var result = await recognizer.RecognizeOnceAsync();

                // Checks result.
                if (result.Reason == ResultReason.RecognizedSpeech)
                {
                    Console.WriteLine($"RECOGNIZED Text: {result.Text}");
                    Console.WriteLine("PRONUNCIATION ASSESSMENT RESULTS:");

                    var pronunciationResultJson = result.Properties.GetProperty(PropertyId.SpeechServiceResponse_JsonResult);
                    dynamic resultJson = JsonConvert.DeserializeObject(pronunciationResultJson);
                    Console.WriteLine(resultJson);
                }
                else if (result.Reason == ResultReason.NoMatch)
                {
                    Console.WriteLine($"NOMATCH: Speech could not be recognized.");
                }
                else if (result.Reason == ResultReason.Canceled)
                {
                    var cancellation = CancellationDetails.FromResult(result);
                    Console.WriteLine($"CANCELED: Reason={cancellation.Reason}");

                    if (cancellation.Reason == CancellationReason.Error)
                    {
                        Console.WriteLine($"CANCELED: ErrorCode={cancellation.ErrorCode}");
                        Console.WriteLine($"CANCELED: ErrorDetails={cancellation.ErrorDetails}");
                        Console.WriteLine($"CANCELED: Did you update the subscription info?");
                    }
                }
            }
        }


        public static async Task GetContentResult()
        {
            // Creates an instance of a speech config with specified subscription key and service region.
            // Replace with your own subscription key and service region (e.g., "westus").
            var config = SpeechConfig.FromSubscription("YourSubscriptionKey", "YourServiceRegion");

            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..", "..", "..");
            string topicPath = Path.Combine(basePath, "resources", "Lauren_topic.txt");
            string wavePath = Path.Combine(basePath, "resources", "Lauren_audio.wav");
            string language = "en-US";
            string topic = File.ReadAllText(topicPath);

            var audioConfig = AudioConfig.FromWavFileInput(wavePath);
            var speechRecognizer = new SpeechRecognizer(config, language.Replace("_", "-"), audioConfig);

            var connection = Connection.FromRecognizer(speechRecognizer);

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
                        "SNR",
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
                if (result.Reason == ResultReason.RecognizedSpeech)
                {
                    var pronunciationResultJson = result.Properties.GetProperty(PropertyId.SpeechServiceResponse_JsonResult);

                    Console.WriteLine($"RECOGNIZED TEXT: {result.Text}");
                    dynamic resultJson = JsonConvert.DeserializeObject(pronunciationResultJson);
                    Console.WriteLine(resultJson["NBest"][0]["ContentAssessment"]);
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
