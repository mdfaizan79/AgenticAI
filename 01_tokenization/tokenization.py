import tiktoken;

encoder = tiktoken.encoding_for_model('gpt-4o')

print("Vocan print : ",encoder.n_vocab) #200019

#find the token for each words

text =" Hey , My Name is Faizan"
tokens = encoder.encode(text)
print("Total Tokens: ",tokens) #[41877, 1366, 3673, 7317, 382, 16792, 58544]


#Now decode and see the result


my_tokens =[41877, 1366, 3673, 7317, 382, 16792, 58544]

d_token = encoder.decode(my_tokens)
print("Decoded Tokens: ",d_token) #Hey , My Name is Faizan