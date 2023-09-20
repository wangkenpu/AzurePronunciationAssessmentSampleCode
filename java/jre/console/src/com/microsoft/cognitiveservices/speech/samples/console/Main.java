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

        try {
            String x;
            do {
                System.out.println("");
                System.out.println("Pronunciation Assessment examples");
                System.out.println("");
                System.out.println("Please choose one of the following samples:");
                System.out.println("1. Get the content of pronunciation assessment.");
                System.out.println("");
                System.out.print(prompt);

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
            } while (!x.equals("0"));

            System.out.println("Finishing demo.");
            System.exit(0);
        } catch (Exception ex) {
            System.out.println("Unexpected " + ex.toString());
            System.exit(1);
        }
    }
}
