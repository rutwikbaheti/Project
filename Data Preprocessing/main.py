import pandas as pd

# # Reading Dataset
dataset = pd.read_csv("dataset.csv")

dataset.drop(dataset.index[dataset['prognosis'] == 'GERD'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'AIDS'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Cervical spondylosis'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'hepatitis A'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Hepatitis B'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Hepatitis C'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Hepatitis D'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Hepatitis E'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Heart attack'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == 'Alcoholic hepatitis'], inplace = True)
dataset.drop(dataset.index[dataset['prognosis'] == '(vertigo) Paroymsal  Positional Vertigo'], inplace = True)
dataset=dataset.drop(labels=['ulcers_on_tongue','muscle_wasting','patches_in_throat','yellow_urine','acute_liver_failure','fluid_overload','swelled_lymph_nodes','weakness_in_limbs','extra_marital_contacts','spinning_movements','unsteadiness','receiving_blood_transfusion','receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen','history_of_alcohol_consumption','fluid_overload.1'],axis=1)
dataset.to_csv('data.csv',index=False)

data = pd.read_csv('data.csv')

# Check the NULL values
print(data.isnull().values.any())

# Count the NULL values
print(data.isnull().sum().sum())

# Replace NULL values with zeros
data.fillna(0)

print(data.head())