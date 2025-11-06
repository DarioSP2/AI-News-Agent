# AI News Agent: Keeping an Eye on Companies

This project is a smart assistant that automatically checks for bad news about a list of companies. Think of it as a personal robot that reads the news for you and tells you if anything important happened.

## What it Does

Every week, this robot does the following:

1.  **Reads a List of Companies**: It starts with a simple list of companies you want to watch.
2.  **Scours the News**: It searches the internet for news articles about these companies from the past week.
3.  **Analyzes the News**: It uses artificial intelligence (AI) to figure out if any of the news is about a controversy (like a lawsuit, a scandal, or a big fine).
4.  **Creates a Report**: It summarizes its findings in a simple, easy-to-read report.

## How to Run It (The Easy Way)

To get this robot working, you just need to do two things:

1.  **Install the Tools**: This is like giving the robot its toolbox. You only have to do this once. Open a terminal and type:
    `pip install -r requirements.txt`

2.  **Run the Robot**: Tell the robot to start its weekly check. In the same terminal, type:
    `python3 -m src.main`

That's it! The robot will start working and will create a folder called `output` with its reports.

## What You Get

After the robot is finished, you'll find these files in the `output` folder:

*   `report-....json`: A detailed computer-readable file with all the findings.
*   `incidents-....csv`: A simple spreadsheet (you can open this with Excel) listing all the bad news it found.
*   `email_body-....html`: A file you can open in your web browser that shows a summary of the report, ready to be sent as an email.

This project helps you stay informed about the companies you care about, without having to read all the news yourself.
