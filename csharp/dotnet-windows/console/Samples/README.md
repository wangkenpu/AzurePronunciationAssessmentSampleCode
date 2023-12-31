# C# Console app for .NET Framework on Windows

This sample demonstrates various forms of pronunciation assessment using the Speech SDK for C#.
It runs under the .NET Framework 4.7.2 (or above) on Windows.

## Prerequisites

* A subscription key for the Speech service. See [Try the speech service for free](https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started).
* A Windows PC; some sample scenarios require a working microphone.
* [Microsoft Visual Studio 2017](https://www.visualstudio.com/), Community Edition or higher.
* The **.NET desktop development** workload in Visual Studio.
  You can enable it in **Tools** \> **Get Tools and Features**.

## Build the sample

* **By building this sample you will download the Microsoft Cognitive Services Speech SDK. By downloading you acknowledge its license, see [Speech SDK license agreement](https://aka.ms/csspeech/license).**
* [Download the sample code to your development PC.](/README.md#get-the-samples)

  > **Note:** make sure to download the complete set of samples, not just this directory.

* Start Microsoft Visual Studio 2017 and select **File** \> **Open** \> **Project/Solution**.
* Navigate to the folder containing this sample, and select the solution file contained within it.
* To tailor the sample to your configuration, use search and replace across the whole solution (for example, via **Edit** \> **Find and Replace** \> **Quick Replace**) to update the following strings:

  * `YourSubscriptionKey`: replace with your subscription key.
  * `YourServiceRegion`: replace with the [region](https://aka.ms/csspeech/region) your subscription is associated with.
    For example, `westus` or `northeurope`.
  * `ScenarioId`: scenario ID will be assigned by product team ("" is the default value for the general model)
  * Some samples require audio files to be present. Put appropriate audio files somewhere on your file system
* Set the active solution configuration and platform to the desired values under **Build** \> **Configuration Manager**:
  * On a 64-bit Windows installation, choose `x64` as active solution platform.
  * On a 32-bit Windows installation, choose `x86` as active solution platform.
* Press Ctrl+Shift+B, or select **Build** \> **Build Solution**.

## Run the sample

To debug the app and then run it, press F5 or use **Debug** \> **Start Debugging**. To run the app without debugging, press Ctrl+F5 or use **Debug** \> **Start Without Debugging**.

  > **Note:** please try cleaning the solution and then rebuild if encountering the issue -- "System.DllNotFoundException"

## References

* [.NET Core on Windows version of this sample](../../dotnet-windows/console)
* [Speech SDK API reference for C#](https://aka.ms/csspeech/csharpref)
