//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

package com.microsoft.cognitiveservices.speech.samples.console;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.io.StringReader;
import jakarta.json.Json;
import jakarta.json.JsonArray;
import jakarta.json.JsonObject;
import jakarta.json.JsonReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

// <toplevel>
import com.microsoft.cognitiveservices.speech.*;
import com.microsoft.cognitiveservices.speech.audio.*;
// </toplevel>

//@SuppressWarnings("resource") // scanner
public class SpeechRecognitionSamples {
	// Replace with your own subscription key and service region (e.g., "westus").
	static String serviceSubscriptionKey = "YourSubscriptionKey";
	static String serviceRegion = "YourServiceRegion";

    // Speech recognition from microphone.
    public static void recognitionContentContinuous() throws InterruptedException, ExecutionException, IOException 
    {
        // Creates an instance of a speech config with specified subscription key and service region.
        SpeechConfig speechConfig = SpeechConfig.fromSubscription(serviceSubscriptionKey, serviceRegion);

        String language = "en-US";
        
        Path currentDirectory = Paths.get(System.getProperty("user.dir"));      
        //basePath
        Path basePath = currentDirectory.resolve("..").resolve("..").resolve("..");       
        //topicPath
        Path topicPath = basePath.resolve("resources").resolve("Lauren_topic.txt");      
        //wavePath
        Path wavePath = basePath.resolve("resources").resolve("Lauren_audio.wav");
        
        String topic = Files.readString(topicPath);
        
        //provide a WAV file as an example. Replace it with your own.
        AudioConfig audioConfig = AudioConfig.fromWavFileInput(wavePath.toString());

        // Creates a speech recognizer using file as audio input
        SpeechRecognizer speechRecognizer = new SpeechRecognizer(speechConfig, language, audioConfig);
        
        Connection connect = Connection.fromRecognizer(speechRecognizer);
        connect.setMessageProperty("speech.context", "phraseDetection", "{\"enrichment\":{\"pronunciationAssessment\":{\"referenceText\":\"\",\"gradingSystem\":\"HundredMark\",\"granularity\":\"Word\",\"dimension\":\"Comprehensive\",\"enableMiscue\":\"False\"},\"contentAssessment\":{\"topic\":\""+topic+"\"}}}");
        connect.setMessageProperty("speech.context", "phraseOutput", "{\"format\":\"Detailed\",\"detailed\":{\"options\":[\"WordTimings\",\"PronunciationAssessment\",\"ContentAssessment\",\"SNR\"]}}");

        List<String> jsonResults = new ArrayList<>();
        // Semaphore used to signal the call to stop continuous recognition (following either a session ended or a cancelled event)
        final Semaphore doneSemaphone = new Semaphore(0);

        // Subscribes to events.
        speechRecognizer.recognized.addEventListener((s, e) -> {
            if (e.getResult().getReason() == ResultReason.RecognizedSpeech) {
                System.out.println(" RECOGNIZED: Text = " + e.getResult().getText());
                String jString = e.getResult().getProperties().getProperty(PropertyId.SpeechServiceResponse_JsonResult);
                jsonResults.add(jString);
            }
            else if (e.getResult().getReason() == ResultReason.NoMatch) {
            	System.out.println(" NOMATCH: Speech could not be recognized.");               
            }
        });

        speechRecognizer.canceled.addEventListener((s, e) -> {
            System.out.println(" CANCELED: Reason = " + e.getReason());
            if (e.getReason() == CancellationReason.Error) {
                System.out.println(" CANCELED: ErrorCode = " + e.getErrorCode());
                System.out.println(" CANCELED: ErrorDetails = " + e.getErrorDetails());
                System.out.println(" CANCELED: Did you update the subscription info?");
            }
            doneSemaphone.release();
        });

        speechRecognizer.sessionStarted.addEventListener((s, e) -> {
            System.out.println("\n Session started event.");
        });

        speechRecognizer.sessionStopped.addEventListener((s, e) -> {
            System.out.println("\n Session stopped event.");
            doneSemaphone.release();
        });

        // Starts continuous recognition and wait for processing to end
        System.out.println(" Recognizing from WAV file... please wait");
        speechRecognizer.startContinuousRecognitionAsync().get();
        doneSemaphone.tryAcquire(30, TimeUnit.SECONDS);

        // Stop continuous recognition
        speechRecognizer.stopContinuousRecognitionAsync().get();

        // These objects must be closed in order to dispose underlying native resources
        speechRecognizer.close();
        speechConfig.close();
        audioConfig.close();
        
        String theLast = jsonResults.get(jsonResults.size() - 1);
        // Convert the JSON string to a JSON object
        JsonReader jsonReader = Json.createReader(new StringReader(theLast));
        JsonArray nbestArray = jsonReader.readObject().getJsonArray("NBest");
        JsonObject firstElement = nbestArray.getJsonObject(0);

        String contentAssessment = firstElement.getJsonObject("ContentAssessment").toString();
        jsonReader.close();
        
        System.out.println("PRONUNCIATION CONTENT ASSESSMENT RESULTS:");
        System.out.println(contentAssessment);
        
    }
}
