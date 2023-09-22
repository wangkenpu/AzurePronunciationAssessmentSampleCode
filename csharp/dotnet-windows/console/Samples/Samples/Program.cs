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
        // Replace with your own subscription key and service region (e.g., "westus").
        private const string ServiceSubscriptionKey = "YourSubscriptionKey";
        private const string ServiceRegion = "YourServiceRegion";

        private static readonly string choose = "Please choose one of the following samples:";
        private static readonly string mainPrompt = "Your choice (or 0 to exit): ";
        private static readonly string exiting = "\nExiting...";
        private static readonly string invalid = "\nInvalid input, choose again.";
        private static readonly string done = "\nDone!";
        static void Main(string[] args)
        {

            ConsoleKeyInfo x;

            do
            {
                Console.WriteLine("");
                Console.WriteLine("Pronunciation Assessment examples");
                Console.WriteLine("");
                Console.WriteLine(choose);
                Console.WriteLine("");
                Console.WriteLine("1. Pronunciation Assessment with Json configure.");
                Console.WriteLine("2. Pronunciation Assessment with Content Score.");
                Console.WriteLine("");
                Console.Write(mainPrompt);

                x = Console.ReadKey();
                Console.WriteLine("");
                bool sampleWasRun = true;

                switch (x.Key)
                {
                    case ConsoleKey.D1:
                    case ConsoleKey.NumPad1:
                        GetAssessmentResultWithJsonConfig().Wait();
                        break;
                    case ConsoleKey.D2:
                    case ConsoleKey.NumPad2:
                        GetContentResult().Wait();
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
        public static async Task GetAssessmentResultWithJsonConfig()
        {
            // Creates an instance of a speech config with specified subscription key and service region.
            // Replace with your own subscription key and service region (e.g., "westus").
            var config = SpeechConfig.FromSubscription(ServiceSubscriptionKey, ServiceRegion);

            // Replace the language with your language in BCP-47 format, e.g., en-US.
            var language = "en-US";

            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..", "..", "..");
            string scriptPath = Path.Combine(basePath, "resources", "weather_script.txt");
            string wavePath = Path.Combine(basePath, "resources", "weather_audio.wav");
            string referenceText = File.ReadAllText(scriptPath);

            // Creates an instance of audio config from an audio file
            var audioConfig = AudioConfig.FromWavFileInput(wavePath);

            // Create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
            var enableMiscue = true;
            var enableProsodyAssessment = true;
            string scenarioId = "";  // # scenario ID will be assigned by product team, by default it is empty string.
            string jsonConfig = "{\"GradingSystem\":\"HundredMark\",\"Granularity\":\"Phoneme\",\"EnableMiscue\":\"" + enableMiscue + "\", \"EnableProsodyAssessment\":\"" + enableProsodyAssessment + "\", \"ScenarioId\":\"" + scenarioId + "\"}";
            var pronunciationConfig = PronunciationAssessmentConfig.FromJson(jsonConfig);
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
                    Console.WriteLine(pronunciationResultJson);
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
            var config = SpeechConfig.FromSubscription(ServiceSubscriptionKey, ServiceRegion);

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

            var done = false;
            var fullRecognizedText = "";

            speechRecognizer.SessionStopped += (s, e) => {
                Console.WriteLine("ClOSING on {0}", e);
                done = true;
            };

            speechRecognizer.Canceled += (s, e) => {
                Console.WriteLine("ClOSING on {0}", e);
                done = true;
            };

            connection.MessageReceived += (s, e) =>
            {
                if (e.Message.IsTextMessage())
                {
                    var messageText = e.Message.GetTextMessage();
                    var json = Newtonsoft.Json.Linq.JObject.Parse(messageText);
                    if (json.ContainsKey("NBest"))
                    {
                        if (json["NBest"][0]["Display"].ToString().Trim().Length > 1)
                        {
                            var recognizedText = json["DisplayText"];
                            fullRecognizedText += $" {recognizedText}";
                            Console.WriteLine($"Pronuciation Assessment Results for: {recognizedText}");
                        }
                        else
                        {
                            Console.WriteLine($"Content Assessment Results for: {fullRecognizedText}");
                        }
                        string jsonText = JsonConvert.SerializeObject(json, Newtonsoft.Json.Formatting.Indented, new JsonSerializerSettings());
                        Console.WriteLine(jsonText);
                    }
                }
            };

            // Starts continuous recognition.
            await speechRecognizer.StartContinuousRecognitionAsync().ConfigureAwait(false);

            while (!done)
            {
                // Allow the program to run and process results continuously.
                await Task.Delay(1000); // Adjust the delay as needed.
            }

            // Waits for completion.
            await speechRecognizer.StopContinuousRecognitionAsync().ConfigureAwait(false);
        }
    }
}
