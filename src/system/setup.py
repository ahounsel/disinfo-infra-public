from setuptools import setup

setup(name='disinfo_net',
      version=0.1,
      author_email='example@example.com',
      license='mit',
      packages=['disinfo_net', 'disinfo_net/orchestrate'],
      scripts=['bin/disinfo_net_data_fetch.py',  
               'bin/disinfo_net_train_classifier.py' ,'bin/disinfo_net_classify.py'],
      include_package_data=True
    )
