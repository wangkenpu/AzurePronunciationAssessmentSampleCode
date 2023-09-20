package com.microsoft.cognitiveservices.speech.samples.console;

import java.util.Scanner;

//
// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
//

@SuppressWarnings("resource") // scanner
public class Main {

    public static void main(String[] args) {
        String prompt = "Your choice (0: Stop): ";

        System.out.println(" 1. Get the content of pronunciation assessment.");

        System.out.print(prompt);

        try {
            String x;
            do {
                x = new Scanner(System.in).nextLine();
                System.out.println("");
                switch (x.toLowerCase()) {
                case "1":
                    SpeechRecognitionSamples.recognitionContentContinuous();
                    break;
                case "0":
                    System.out.println("Exiting...");
                    break;
                }
                System.out.println("\nExecution done. " + prompt);
            } while (!x.equals("0"));

            System.out.println("Finishing demo.");
            System.exit(0);
        } catch (Exception ex) {
            System.out.println("Unexpected " + ex.toString());
            System.exit(1);
        }
    }
}
