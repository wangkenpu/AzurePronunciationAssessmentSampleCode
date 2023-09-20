# JavaScript Speech Recognition, Content assessment Sample for Node.js

This sample demonstrates how to recognize speech with the Speech SDK for JavaScript on Node.js. It is based on the [Microsoft Cognitive Services Speech SDK for JavaScript](https://aka.ms/csspeech/npmpackage).
See [this article](https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started-speech-to-text?pivots=programming-language-nodejs) for introductory information on the Speech SDK for JavaScript on Node.js.

## Prerequisites

* A subscription key for the Speech service. See [Try the speech service for free](https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started).
* For intent recognition: an *endpoint* subscription key for the [Language Understanding Intelligent Service (LUIS)](https://www.luis.ai/home), and an application ID.
* A [Node.js](https://nodejs.org) compatible device.

## Prepare the sample

* Update the following strings in the `main.js` file with your configuration:
  * `YourSubscriptionKey`: replace with your subscription key.
  * `YourServiceRegion`: replace with the [region](https://aka.ms/csspeech/region) your subscription is associated with. For example, `westeurope` or `eastasia`.
  * Your language for speech recognition, if you want to change the default `en-us` (American English).
  * `YourAudioFile.wav`: An audio file with speech to be recognized. The format is 16khz sample rate, mono, 16-bit per sample PCM. See for example a file named `Lauren_audio.wav` located in several folders in this repository. Make sure the above language settings matches the language spoken in the WAV file. Note: This sample assumes there is a 44 bit wav header on the file and skips those bytes in the stream.
  * `YourTopicFile.wav`: A text file to be recognized. See for example a file named `Lauren_topic.txt` located in several folders in this repository.

* Run `npm install` to install any required dependency on your computer.

## Run the sample

run the following command in the terminal:

```shell
node main.js
```

## References

* [Node.js quickstart article on the SDK documentation site](https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-js-node)
* [Speech SDK API reference for JavaScript](https://aka.ms/csspeech/javascriptref)
