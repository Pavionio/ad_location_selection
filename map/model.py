import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.preprocessing import (OneHotEncoder, FunctionTransformer)
from sklearn.ensemble import (ExtraTreesRegressor, VotingRegressor, RandomForestRegressor)
from sklearn.svm import LinearSVR
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics.pairwise import euclidean_distances
import ast
import lightgbm as lgb


class DensityRegressor():
    def __init__(self):
        train = pd.read_json('train_data.json')
        for cnt in ['gender', 'ageFrom', 'ageTo', 'income']:
            def x_lab(x):
                return x[cnt]

            train[cnt] = train['targetAudience'].apply(lambda x: x[cnt])
        train['ageFrom,ageTo'] = train.apply(lambda x: [x['ageFrom'], x['ageTo']], axis=1)
        self.gdic = dict(zip(train['gender'].unique(), [['female', 'male'], ['female'], ['male']]))
        locs = pd.Series(pd.Series(train['points'].agg(sum)).astype(str).unique()).apply(lambda x: ast.literal_eval(x))
        self.locs = locs[euclidean_distances(np.array([locs.apply(lambda x: float(x['lat'])).tolist(),
                                                       locs.apply(lambda x: float(x['lon'])).tolist()]).T).mean(
            axis=1) < 2]
        self.train = train
        pipe0 = Pipeline([('input', ColumnTransformer([
            ('oe', OneHotEncoder(handle_unknown='ignore'), ['income']),
            ('gender', CountVectorizer(tokenizer=lambda x: self.gdic[x], token_pattern=None,
                                       lowercase=False), 'gender'),
            ('ageFrom,ageTo',
             CountVectorizer(tokenizer=lambda x: [str(i) for i in range(x[0], x[1] + 1)], token_pattern=None,
                             lowercase=False), 'ageFrom,ageTo'),
            ('coordinates', CountVectorizer(tokenizer=lambda x: [str(i) for i in x], token_pattern=None,
                                            lowercase=False), 'points')
        ])),
                          ('tfidf', TfidfTransformer()),
                          ('cls', LinearSVR(C=10., loss='squared_epsilon_insensitive'))])
        pipe1 = Pipeline([('input', ColumnTransformer([
            ('ageFrom,ageTo',
             CountVectorizer(tokenizer=lambda x: [str(i) for i in range(x[0], x[1] + 1)], token_pattern=None,
                             lowercase=False), 'ageFrom,ageTo'),
            ('gender', CountVectorizer(tokenizer=lambda x: self.gdic[x], token_pattern=None,
                                       lowercase=False), 'gender'),
            ('income', CountVectorizer(analyzer='char',
                                       lowercase=False), 'income'),
            ('coordinates',
             CountVectorizer(tokenizer=lambda x: [str({i[j] for j in ['lat', 'lon']}) for i in x], token_pattern=None,
                             lowercase=False), 'points')

        ])),
                          ('cls', RandomForestRegressor(n_estimators=100))])
        pipe2 = Pipeline([('input', ColumnTransformer([

            ('passthrough', FunctionTransformer(lambda x: x.astype(float)), ['ageFrom', 'ageTo']),
            ('gender', CountVectorizer(tokenizer=lambda x: self.gdic[x], token_pattern=None,
                                       lowercase=False), 'gender'),
            ('income', CountVectorizer(analyzer='char',
                                       lowercase=False), 'income'),
            ('coordinates',
             CountVectorizer(tokenizer=lambda x: [str({i[j] for j in ['lat', 'lon']}) for i in x], token_pattern=None,
                             lowercase=False), 'points')
        ])),
                          ('cls', lgb.sklearn.LGBMRegressor(n_estimators=250))])
        pipe3 = Pipeline([('input', ColumnTransformer([
            ('ageFrom,ageTo',
             CountVectorizer(tokenizer=lambda x: [str(i) for i in range(x[0], x[1] + 1)], token_pattern=None,
                             lowercase=False), 'ageFrom,ageTo'),
            ('gender', CountVectorizer(tokenizer=lambda x: self.gdic[x], token_pattern=None,
                                       lowercase=False), 'gender'),
            ('income', CountVectorizer(analyzer='char',
                                       lowercase=False), 'income'),
            ('coordinates',
             CountVectorizer(tokenizer=lambda x: [str({i[j] for j in ['lat', 'lon']}) for i in x], token_pattern=None,
                             lowercase=False), 'points')

        ])),
                          ('cls', ExtraTreesRegressor(n_estimators=100))])
        self.vr = VotingRegressor([('0', pipe0), ('1', pipe1), ('2', pipe2), ('3', pipe3)]).fit(train, train['value'])

    def get_den(self, aud):
        den = pd.DataFrame({'points': self.locs.apply(lambda x: [x]).tolist()})
        den['targetAudience'] = [aud] * len(den)
        for cnt in ['gender', 'ageFrom', 'ageTo', 'income']:
            den[cnt] = den['targetAudience'].apply(lambda x: x[cnt])
        den['ageFrom,ageTo'] = den.apply(lambda x: [x['ageFrom'], x['ageTo']], axis=1)
        return den

    def predict_points(self, aud, points=None, sorted=True, top_k=None, score=False):
        '''Предсказать точки размещения для заданной целевой аудитории, параметры:
        aud - целевая аудитория в виде словаря
        {'name': 'All 18+', 'gender': 'female', 'ageFrom': 18, 'ageTo': 100, 'income': 'abc'};
        points - подмножество точек в виде серии словарей
        0      {'lat': '55.573691', 'lon': '37.631423', 'azim...
        1      {'lat': '55.584765', 'lon': '37.712454', 'azim...;
        sorted - сортировать;
        top_k - выбрать лучшие k точек;
        score - добавить скор для суммы полученных точек
        (в виде кортежа с датафрэймом точек).'''
        if points is None:
            den = pd.DataFrame({'points': self.locs.apply(lambda x: [x]).tolist()})
        else:
            den = pd.DataFrame({'points': points.apply(lambda x: [x]).tolist()})
        den['targetAudience'] = [aud] * len(den)
        for cnt in ['gender', 'ageFrom', 'ageTo', 'income']:
            den[cnt] = den['targetAudience'].apply(lambda x: x[cnt])
        den['ageFrom,ageTo'] = den.apply(lambda x: [x['ageFrom'], x['ageTo']], axis=1)
        weights = self.vr.predict(den)
        out = pd.DataFrame({'lat': den['points'].apply(lambda x: float(x[0]['lat']))[weights > 0].values,
                            'lon': den['points'].apply(lambda x: float(x[0]['lon']))[weights > 0].values,
                            'weights': weights[weights > 0]})
        if points is None:
            out['weights'] = 100 * out['weights'] / out['weights'].sum()
        else:
            out['weights'] = out['weights'] / max(100, out['weights'].sum())
        if sorted:
            out = out.sort_values(by='weights', ascending=False)
        if top_k is not None:
            print(out)
            out = out.iloc[:top_k]
            den2 = den.iloc[:1]
            den2['points'] = [den['points'].apply(lambda x: x[0]).loc[out.index].tolist()]
            score_ = min(100., self.vr.predict(den2)[0])
            out['weights'] = score_ * out['weights'] / out['weights'].sum()
        if (score) and (top_k is not None):
            out = (out, score_)
        return out

    def predict(self, test):
        '''Сделать предсказание на тестовом
        наборе данных.'''
        for cnt in ['gender', 'ageFrom', 'ageTo', 'income']:
            test[cnt] = test['targetAudience'].apply(lambda x: x[cnt])
        test['ageFrom,ageTo'] = test.apply(lambda x: [x['ageFrom'], x['ageTo']], axis=1)
        return self.vr.predict(test)
