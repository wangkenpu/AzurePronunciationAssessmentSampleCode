using System;
using System.IO;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using DiffPlex;
using DiffPlex.DiffBuilder;
using DiffPlex.DiffBuilder.Model;

using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.CognitiveServices.Speech.PronunciationAssessment;

namespace Samples
{
    class Program
    {
        // Replace with your own subscription key and service region (e.g., "westus").
        private const string ServiceSubscriptionKey = "";
        private const string ServiceRegion = "";

        private const double ProsodyThreshold = 0.1;

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
                Console.WriteLine("3. Pronunciation Assessment with Continuous.");
                Console.WriteLine("4. Pronunciation Assessment with Microphone.");
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
                    case ConsoleKey.D3:
                    case ConsoleKey.NumPad3:
                        PronunciationAssessmentContinuousWithFile().Wait();
                        break;
                    case ConsoleKey.D4:
                    case ConsoleKey.NumPad4:
                        PronunciationAssessmentWithMicrophoneAsync().Wait();
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

        // Pronunciation assessment continous from file
        // See more information at https://aka.ms/csspeech/pa
        public static async Task PronunciationAssessmentContinuousWithFile()
        {
            // Creates an instance of a speech config with specified subscription key and service region.
            // Replace with your own subscription key and service region (e.g., "westus").
            var config = SpeechConfig.FromSubscription(ServiceSubscriptionKey, ServiceRegion);

            // Creates a speech recognizer using file as audio input. 
            string basePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..", "..", "..");
            string wavePath = Path.Combine(basePath, "resources", "weather_audio.wav");
            using (var audioInput = AudioConfig.FromWavFileInput(wavePath))
            {
                // Switch to other languages for example Spanish, change language "en-US" to "es-ES". Language name is not case sensitive.
                var language = "en-US";

                using (var recognizer = new SpeechRecognizer(config, language, audioInput))
                {
                    var referenceText = "what's the weather like";

                    bool enableMiscue = true;

                    var pronConfig = new PronunciationAssessmentConfig(referenceText, GradingSystem.HundredMark, Granularity.Phoneme, enableMiscue);

                    pronConfig.EnableProsodyAssessment();

                    pronConfig.ApplyTo(recognizer);

                    var recognizedWords = new List<string>();
                    var pronWords = new List<Word>();
                    var finalWords = new List<Word>();
                    var fluency_scores = new List<double>();
                    var prosody_scores = new List<double>();
                    var durations = new List<int>();
                    var done = false;

                    recognizer.SessionStopped += (s, e) => {
                        Console.WriteLine("ClOSING on {0}", e);
                        done = true;
                    };

                    recognizer.Canceled += (s, e) => {
                        Console.WriteLine("ClOSING on {0}", e);
                        done = true;
                    };

                    recognizer.Recognized += (s, e) => {
                        Console.WriteLine($"RECOGNIZED: Text={e.Result.Text}");
                        var pronResult = PronunciationAssessmentResult.FromResult(e.Result);
                        Console.WriteLine($"    Accuracy score: {pronResult.AccuracyScore}, prosody score:{pronResult.ProsodyScore}, pronunciation score: {pronResult.PronunciationScore}, completeness score: {pronResult.CompletenessScore}, fluency score: {pronResult.FluencyScore}");

                        var responseJson = e.Result.Properties.GetProperty(PropertyId.SpeechServiceResponse_JsonResult);

                        var doc = JObject.Parse(responseJson);

                        var words = doc["NBest"][0]["Words"];
                        foreach (JObject item in words)
                        {
                            string word_item = item["Word"].ToObject<string>();
                            JObject pa = (JObject)item["PronunciationAssessment"];

                            string errorType_item = pa["ErrorType"].ToObject<string>();
                            bool accuracyScore_exist = pa.TryGetValue("AccuracyScore", out JToken accuracyScore_element);

                            double accuracyScore_item = 0.0d;

                            if (accuracyScore_exist)
                            {
                                accuracyScore_item = accuracyScore_element.ToObject<double>();
                            }

                            bool feedback_exist = pa.TryGetValue("Feedback", out JToken feedback_item);

                            JToken prosody_item = null;

                            if (feedback_exist)
                            {
                                prosody_item = feedback_item["Prosody"].DeepClone();
                            }

                            var newWord = new Word(word_item, errorType_item, accuracyScore_item, prosody_item);
                            pronWords.Add(newWord);
                        }

                        fluency_scores.Add(pronResult.FluencyScore);
                        prosody_scores.Add(pronResult.ProsodyScore);

                        foreach (var result in e.Result.Best())
                        {
                            durations.Add(result.Words.Sum(item => item.Duration));
                            recognizedWords.AddRange(result.Words.Select(item => item.Word).ToList());

                        }
                    };

                    // Starts continuous recognition.
                    await recognizer.StartContinuousRecognitionAsync().ConfigureAwait(false);

                    while (!done)
                    {
                        // Allow the program to run and process results continuously.
                        await Task.Delay(1000); // Adjust the delay as needed.
                    }

                    // Waits for completion.
                    await recognizer.StopContinuousRecognitionAsync().ConfigureAwait(false);

                    // For continuous pronunciation assessment mode, the service won't return the words with `Insertion` or `Omission`
                    // even if miscue is enabled.
                    // We need to compare with the reference text after received all recognized words to get these error words.
                    string[] referenceWords = referenceText.ToLower().Split(' ');
                    List<string> referenceWordsList = new List<string>(referenceWords);

                    for (int j = 0; j < referenceWords.Length; j++)
                    {
                        referenceWords[j] = Regex.Replace(referenceWords[j], "^[\\p{P}\\s]+|[\\p{P}\\s]+$", "");
                    }

                    // Diff the reference and recognized string
                    var differ = new Differ();
                    var inlineBuilder = new InlineDiffBuilder(differ);
                    var diffModel = inlineBuilder.BuildDiffModel(string.Join("\n", referenceWords), string.Join("\n", recognizedWords));

                    int recognizedIdx = 0;
                    int referenceIdx = 0;

                    foreach (var delta in diffModel.Lines)
                    {

                        if (delta.Type == ChangeType.Unchanged)
                        {
                            Word w_same = pronWords[recognizedIdx];
                            w_same.HasPunctuation = HasPunctuation(referenceIdx, referenceWordsList);

                            finalWords.Add(w_same);

                            recognizedIdx += 1;
                            referenceIdx += 1;
                        }

                        if (delta.Type == ChangeType.Deleted || delta.Type == ChangeType.Modified)
                        {
                            if (enableMiscue)
                            {
                                var word = new Word(delta.Text, "Omission", null);
                                word.HasPunctuation = HasPunctuation(referenceIdx, referenceWordsList);

                                finalWords.Add(word);
                            }

                            referenceIdx += 1;
                        }

                        if (delta.Type == ChangeType.Inserted || delta.Type == ChangeType.Modified)
                        {
                            Word w = pronWords[recognizedIdx];
                            if (enableMiscue)
                            {
                                if (w.ErrorType == "None")
                                {
                                    w.ErrorType = "Insertion";
                                    finalWords.Add(w);
                                }
                            }
                            else
                            {
                                finalWords.Add(w);
                            }

                            recognizedIdx += 1;
                        }
                    }

                    // We can calculate whole accuracy by averaging
                    var filteredWords = finalWords.Where(item => item.ErrorType != "Insertion");
                    var accuracyScore = filteredWords.Sum(item => item.AccuracyScore) / filteredWords.Count();

                    // Recalculate the prosody score by averaging
                    var prosodyScore = prosody_scores.Average();

                    // Recalculate fluency score
                    var fluencyScore = fluency_scores.Zip(durations, (x, y) => x * y).Sum() / durations.Sum();

                    // Calculate whole completeness score
                    var completenessScore = (double)pronWords.Count(item => item.ErrorType == "None") / referenceWords.Length * 100;
                    completenessScore = completenessScore <= 100 ? completenessScore : 100;

                    Console.WriteLine("Paragraph accuracy score: {0}, prosody score: {1} completeness score: {2}, fluency score: {3}", accuracyScore, prosodyScore, completenessScore, fluencyScore);

                    for (int idx = 0; idx < finalWords.Count(); idx++)
                    {
                        Word word = finalWords[idx];
                        bool signal = idx > 0 && finalWords[idx - 1].HasPunctuation;
                        string errorType = getFinalErrorType(word.ErrorType, word.Prosody, signal, ProsodyThreshold);
                        Console.WriteLine("{0}: word: {1}\taccuracy score: {2}\terror type: {3}",
                            idx + 1, word.WordText, word.AccuracyScore, errorType);
                    }
                }
            }
        }

        // Pronunciation assessment with microphone as audio input.
        // See more information at https://aka.ms/csspeech/pa
        public static async Task PronunciationAssessmentWithMicrophoneAsync()
        {
            // Creates an instance of a speech config with specified subscription key and service region.
            // Replace with your own subscription key and service region (e.g., "westus").
            var config = SpeechConfig.FromSubscription(ServiceSubscriptionKey, ServiceRegion);

            // Replace the language with your language in BCP-47 format, e.g., en-US.
            var language = "en-US";

            // The pronunciation assessment service has a longer default end silence timeout (5 seconds) than normal STT
            // as the pronunciation assessment is widely used in education scenario where kids have longer break in reading.
            // You can adjust the end silence timeout based on your real scenario.
            config.SetProperty(PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "3000");

            var referenceText = "";
            // create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
            var pronunciationConfig = new PronunciationAssessmentConfig(referenceText,
                GradingSystem.HundredMark, Granularity.Phoneme, true);

            pronunciationConfig.EnableProsodyAssessment();

            // Creates a speech recognizer for the specified language, using microphone as audio input.
            using (var recognizer = new SpeechRecognizer(config, language))
            {
                while (true)
                {
                    // Receives reference text from console input.
                    Console.WriteLine("Enter reference text you want to assess, or enter empty text to exit.");
                    Console.Write("> ");
                    referenceText = Console.ReadLine();
                    if (string.IsNullOrEmpty(referenceText))
                    {
                        break;
                    }

                    List<string> referenceTextList = new List<string>(referenceText.Split(' '));

                    pronunciationConfig.ReferenceText = referenceText;

                    // Starts recognizing.
                    Console.WriteLine($"Read out \"{referenceText}\" for pronunciation assessment ...");

                    pronunciationConfig.ApplyTo(recognizer);

                    // Starts speech recognition, and returns after a single utterance is recognized.
                    // For long-running multi-utterance recognition, use StartContinuousRecognitionAsync() instead.
                    var result = await recognizer.RecognizeOnceAsync().ConfigureAwait(false);

                    // Checks result.
                    if (result.Reason == ResultReason.RecognizedSpeech)
                    {
                        Console.WriteLine($"RECOGNIZED: Text={result.Text}");
                        Console.WriteLine("  PRONUNCIATION ASSESSMENT RESULTS:");

                        var pronunciationResult = PronunciationAssessmentResult.FromResult(result);
                        Console.WriteLine(
                            $"    Accuracy score: {pronunciationResult.AccuracyScore}, Prosody Score: {pronunciationResult.ProsodyScore}, Pronunciation score: {pronunciationResult.PronunciationScore}, Completeness score : {pronunciationResult.CompletenessScore}, FluencyScore: {pronunciationResult.FluencyScore}");

                        Console.WriteLine("  Word-level details:");
                        var responseJson = result.Properties.GetProperty(PropertyId.SpeechServiceResponse_JsonResult);

                        var doc = JObject.Parse(responseJson);
                        var words = doc["NBest"][0]["Words"];

                        int referencePosition = 0;
                        List<Word> pronWords = new List<Word>();

                        foreach (JObject item in words)
                        {
                            string word_item = item["Word"].ToObject<string>();
                            JObject pa = (JObject)item["PronunciationAssessment"];

                            string errorType_item = pa["ErrorType"].ToObject<string>();
                            bool accuracyScore_exist = pa.TryGetValue("AccuracyScore", out JToken accuracyScore_element);

                            double accuracyScore_item = 0.0d;

                            if (accuracyScore_exist)
                            {
                                accuracyScore_item = accuracyScore_element.ToObject<double>();
                            }

                            bool feedback_exist = pa.TryGetValue("Feedback", out JToken feedback_item);

                            JToken prosody_item = null;

                            if (feedback_exist)
                            {
                                prosody_item = feedback_item["Prosody"].DeepClone();
                            }

                            var newWord = new Word(word_item, errorType_item, accuracyScore_item, prosody_item);

                            if ("Insertion" == errorType_item)
                            {
                                newWord.HasPunctuation = false;
                            }
                            else
                            {
                                newWord.HasPunctuation = HasPunctuation(referencePosition, referenceTextList);
                                referencePosition += 1;
                            }
                            pronWords.Add(newWord);
                        }

                        for (int i = 0; i < pronWords.Count; i++)
                        {
                            var word = pronWords[i];
                            bool word_hasPunctuation = i > 0 && pronWords[i - 1].HasPunctuation;
                            Console.WriteLine($"    Word: {word.WordText}, Accuracy score: {word.AccuracyScore}, Error type: {getFinalErrorType(word.ErrorType, word.Prosody, word_hasPunctuation, ProsodyThreshold)}.");
                        }
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
        }
        public static bool HasPunctuation(int pos, List<string> wordList)
        {
            string word = wordList[pos];
            if (word.Length > 0 && char.IsPunctuation(word[word.Length - 1]))
            {
                return true;
            }
            return false;
        }

        /// <summary>
        /// combine of the error types of word, break and innotation
        /// </summary>
        /// <param name="errorType"> word error type</param>
        /// <param name="prosody"> JsonElement value of prosody </param>
        /// <param name="hasPunctuation">if the former word has punctuation </param>
        /// <param name="threshold"> threshold of confidence of MissingBreak/UnexpectedBreak </param>
        /// <returns>None or combines of error types </returns>
        public static string getFinalErrorType(string errorType, JToken prosody, bool hasPunctuation, double threshold)
        {
            List<string> result = new List<string>();
            if (errorType != "None")
            {
                result.Add(errorType);
            }

            if (prosody != null)
            {
                //JsonElement prosodyValue = prosody.Value;
                JObject break_prosody = (JObject)prosody["Break"];

                string errorType_break = "";
                if (!hasPunctuation)
                {
                    errorType_break = "UnexpectedBreak";
                }
                else
                {
                    errorType_break = "MissingBreak";
                }
                if (break_prosody.TryGetValue(errorType_break, out JToken break_value))
                {
                    double confidence = break_value["Confidence"].ToObject<double>();
                    if (confidence >= threshold)
                    {
                        result.Add(errorType_break);
                    }
                }

                var errorType_intonation = (JArray)prosody["Intonation"]["ErrorTypes"];
                if ((errorType_intonation.Count > 0) && (errorType_intonation[0].ToObject<string>() != "None"))
                {
                    result.Add(errorType_intonation[0].ToObject<string>());
                }
            }

            return result.Count == 0 ? "None" : string.Join(",", result);
        }
    }

    public class Word
    {
        public string WordText { get; set; }
        public string ErrorType { get; set; }
        public double AccuracyScore { get; set; }
        public JToken Prosody { get; set; }
        public bool HasPunctuation { get; set; }

        public Word(string wordText, string errorType, JToken prosody)
        {
            WordText = wordText;
            ErrorType = errorType;
            AccuracyScore = 0;
            Prosody = prosody;
            HasPunctuation = false;
        }

        public Word(string wordText, string errorType, double accuracyScore, JToken prosody) : this(wordText, errorType, prosody)
        {
            AccuracyScore = accuracyScore;
        }
    }
}
