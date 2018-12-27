import pandas as pd


def getUserCorrelation(userId, ratingsSet, correlationMatrix, verbose=False):
    ''' prints a user's top correlated movies for a given set of ratings and a correlation matrix for movies'''
    userRatings = ratingsSet.loc[userId].dropna()
    similarMovies = pd.Series()
    #itterate through the user's ratings and find simmilar movies
    for i in range(0, len(userRatings.index)):
        if verbose:
            print 'Adding similarities for ' + userRatings.index[i]
        similarCandidates = correlationMatrix[userRatings.index[i]].dropna()
        similarCandidates = similarCandidates.map(lambda x: x * userRatings[i])
        similarMovies = similarMovies.append(similarCandidates)

    # we don't want to see duplicates so lets group by and sum to make movies with multiple similarities higher
    similarMovies = similarMovies.groupby(similarMovies.index).sum()
    # gotta sort those similar movies for highest similarity
    #tried to sort in place but had to use higher memory for sort function to work
    similarMovies = similarMovies.sort_values(ascending=False)
    #remove my reviewed movies, who wants to see those ones again?
    #there has to be a better way I'm just not using pandas.drop right
    for i in range(0, len(userRatings.index)):
        try:
            similarMovies = similarMovies.drop(userRatings.index[i])
        # if the movies is not recommended but in reviewed list
        except KeyError:
            if verbose:
                print userRatings.index[i] + ' not found in recommended movies list'
    if verbose:
        print similarMovies.head(10)
    return similarMovies


def main():
    #basic setup with user, movie, review columns setup and data fed into the program
    u_col = ['user_id', 'age', 'sex', 'occupation', 'zipcode']
    users = pd.read_csv('/Users/home/Downloads/ml-100k/u.user', sep='|', names=u_col, usecols=range(4))
    m_col = ['movie_id', 'title']
    movies = pd.read_csv('/Users/home/Downloads/ml-100k/u.item', sep='|', names=m_col, usecols=range(2))
    r_col = ['user_id', 'movie_id', 'rating']
    ratings = pd.read_csv('/Users/home/Downloads/ml-100k/u.data', sep='\t', names=r_col, usecols=range(3))
    #get the ratings for each movie
    movRatings = pd.merge(movies, ratings)
    #get the ratings for each user
    userRatings = movRatings.pivot_table(index=['user_id'], columns=['title'], values='rating')

    #find the correlation between two movies being simmilarly compared with the minimum crossover reviews being 20
    corrMatrix = userRatings.corr(method='pearson', min_periods=20)
    #set of doctors in the dataset
    doctors = users.loc[users['occupation'] == 'doctor']

    #unweighted list of movies that doctors like
    doctorMovies = pd.Series()
    for index, row in doctors.iterrows():
       doctorMovies = doctorMovies.append(getUserCorrelation(row['user_id'], userRatings, corrMatrix))
    doctorMovies = doctorMovies.groupby(doctorMovies.index).sum()
    # gotta sort those similar movies for highest simmilarity
    # tried to sort in place but had to use higher memory for sort function to work
    doctorMovies = doctorMovies.sort_values(ascending=False)
    print 'The top 10 movies for the doctors are'
    print doctorMovies.head(10)
    #print getUserCorrelation(1, userRatings, corrMatrix)


main()