# Email-Handling-Project
My Anthropic API project for tool use. Make claude read and write emails for you!

## Table of Contents

- Getting Started
- Usage
- Contributing
- License
- Contact

## Getting Started

This section will guide you through the prerequisites and installation process to get the project up and running on your local machine.

### Prerequisites
There are currently no prerequisites for this project except a working version of python.

### Installation

Follow these steps to install the project on a Windows machine:

1. Clone the repository:
    ```bash
    git clone https://github.com/LeoFVG/ai-email-assistant.git
    cd ai-email-assistant
    ```
2. Create a conda environment (optional):
    ```bash
    conda create -n ai-email-assistant python=3.12
    conda activate ai-email-assistant
    ```
4. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the main.py file (make sure a proper api key is set in the main.py file):
    ```bash
    python main.py
    ```

## Usage
- When the main function is run you will be prompted to login to your email, if you are using gmail you need to manually activate imap support in your gmail settings for the bot to properly be able to read your emails.
- The bot has the ability to read an email when given a specified increment (e.g "Read my 10th most recent email.").
- The bot has the ability to send an email (e.g. Send an email about Minecraft to example-email@example.com).
- It currently has no chat memory and i am currently working on an open source local version using ollama that will have a lot more features.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## License
This system is available under the MIT license.

## Contact

Leo Voghera - leovoghera@hotmail.com
Project Link: https://github.com/LeoFVG/ai-email-assistant.git
