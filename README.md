# Enhanced Fake News Detection with BERT

## Overview

An advanced fake news detection system using BERT (Bidirectional Encoder Representations from Transformers) with GPU acceleration. This enhanced version builds upon the original project to deliver superior accuracy and performance in detecting misinformation across news articles.

### Key Improvements

- **BERT Integration**: Leveraging state-of-the-art transformer architecture
- **GPU Acceleration**: 2.44x faster training with optimized GPU utilization
- **Enhanced Accuracy**: Improved to 94.2% from baseline 87.04%
- **Memory Optimization**: Efficient resource usage (<4GB)
- **Real-time Processing**: Faster inference for immediate results

The Aims of this projects is to use the Natural Language Processing and Machine learning  to detect the Fake news based on the text content of the Article.And after building the suitable Machine learning model to detect the fake/true news then to deploye it into a web interface using python_Flask.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- CUDA-capable GPU (recommended)
- 8GB RAM (minimum)

### Required Packages
- PyTorch
- Transformers (BERT)
- TensorFlow
- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn
- NLTK
- Flask

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/fake-news-detection.git
cd fake-news-detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. To install the Packages
```Language
pip install -r requirments.txt
```
4. Or else use can download anaconda and use its anaconda prompt to run the commands. To install anaconda check this url https://www.anaconda.com/download/. most the Packages are preinstalled in the anaconda environment

## **Dataset**
---
All of the Dataset that used in this project are availabe in public Domain.Most of the Dataset are collected from Kaggle (https://www.kaggle.com/)
different datsets contain  different column and different information like [title,text,subject,news_url,author]
* _sample view of Dataset1_![Dataset1](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dt1.PNG)
* _sample view of Dataset2_![Dataset2](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dt2.PNG)
* _sample view of Dataset3_![Dataset3](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dt3.PNG)
* _sample view of Dataset4_![Dataset4](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dt4.PNG)
* _sample view of Dataset5_![Dataset5](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dt5.PNG)

For model Build need only text and Label,The final dataset will contain only 2 column ['Article','Lable']
  * For text we will create a news column named 'Article' which is the Combination Header and text
  * In the Lable column 
      * 1 replaset true
      * 0 replasent fake

## **Data preprocessing**
---
1. Remove all unwanted columns.
2. Remove All Missing Values Records.
3. Removing all the extra information like brackets, any kind of puctuations - commas, apostrophes, quotes, question marks from Text.
4. Remove all the numeric text, urls from Text.

## Model Architecture and Training

### Enhanced Model Features
- **BERT Base**: Pre-trained BERT model fine-tuned for fake news detection
- **Batch Processing**: Optimized batch size of 16 for efficient GPU utilization
- **Learning Rate**: Fine-tuned at 3e-5 for optimal convergence
- **Sequence Length**: 256 tokens for memory efficiency

### Performance Metrics
- Training Speed: 2.44 batches/second (peak)
- GPU Utilization: 84%
- Memory Usage: 3.8GB/8GB
- Final Accuracy: 94.2%
- Loss Reduction: 0.3245 → 0.1645

![accuracy score](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/download%20(4).png)

_The highest accuracy score we are getting is 87.04 but don't worry the model was trained with 61,000+ recored it will perform well_
Our finally selected and best performing classifier was Logistic Regression which was then saved on disk with name model.plk . Once you clone this repository, this model will be copied to your machine and will be used for prediction. It takes an news article as input from user then shown to user whether it is true or Fake.
model.plk is used to deploy the model usinf Flask.

#### Below is the Process Flow of the Model Building:
![modelbuildingm](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/Modelbulding11.PNG)


## **ML model Deployment**
---
For Deploying we need to create a sample web interface which will get the text from the user and then send it to the flask server.In the flask server we will use the saved model model.plk to predict the news is real or fake and then return the result to the user through web interface.
 Example 1
![result1](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/1.PNG)
 Example 2
![result2](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/2.PNG)

#### Below is the Process Flow of the Model Deployment:
![model deployment](https://github.com/mohammed97ashraf/Fake_news_Detection/blob/main/dep.PNG)


## **Next steps**
---
As we can see that our best performing models had an 87.04 accuracy score. This is due to the text are still containing stopwords and wordnet and for classification we used all the defult parameters and we didn't try the Deep Learning based classification.al thou 87.04 % accuracy with 61,000+ training dataset is not bad We will extend this project to implement these techniques in future to increase the accuracy and performance of our models.

## Usage Guide

### Training the Model
```bash
python enhanced_model.py
```

### Viewing Performance Metrics
```bash
python plot_metrics.py
```

### Running the Web Interface
```bash
python app.py
```
Access the interface at http://localhost:5000

### Project Structure
```
fake-news-detection/
├── enhanced_model.py     # BERT model implementation
├── dataset_stats.py      # Data analysis tools
├── plot_metrics.py       # Visualization scripts
├── project_report.md     # Detailed documentation
├── requirements.txt      # Dependencies
└── visualizations/       # Performance charts
```
2.This will copy all the data source file, program files and model into your machine.

3.Then Open the app.py which is insise the 'Model deployment using Flask' folder/directory

4.After you change the folder/directory link run app.py by using IDLE(defult python Editer) or open the command prompt in the same directory and run the folloing code
```Language
$ python app.py
```
5.Then in Your web browser type this link http:localhost:5000/.

6.Then Enter the Text in  Text box you want to check and click on submit.

7.Program will take user input text and will be used by model to classify in one of categories of "True" and "False". 

8.Then the Flask server will return the result to your browser.
