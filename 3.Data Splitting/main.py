import pandas as pd
from sklearn.model_selection import train_test_split

#Reading dataset
data = pd.read_csv('data.csv')

# Split the data into train and test set
training,testing = train_test_split(data, test_size=0.10, random_state=0)

# Save the data
training.to_csv('Training.csv',index=False)
testing.to_csv('Testing.csv',index=False)

print(data.head())