# Software Requirements
1. Vs Code (For Running the code )
2. PostgreSQL and pgadmin4 (Database)

# Steps to setup


first delete .Git file in DatasetVideo, TrainingImage and VotingDSVideo, if there is no .git file leave as it is

1. Open terminal and create a environment , SYNTAX:  python -m venv env        (Remember that it will create a folder named env where we store all the python packages needed for this project)

2. To activate it, SYNTAX: env\scripts\activate     (Remember that you should always activate this syntax whenever you run this project)

3. After activating, it will display (env) in green colour before the terminal path

4. Once it is done install the packages given below in terminal 
             
            * pip install scikit-learn
            * pip install certifi
            * pip install chardet
            * pip install Django
            * pip install facerecog
            * pip install idna
            * pip install opencv-contrib-python
            * pip install pandas
            * pip install Pillow
            * pip install psycopg2
            * pip install requests
            * pip install setuptools
            * pip install opencv-python

5. Once u setup postgre and pgadmin4, go to pgadmin4 software it will ask you password which is your laptop password and on the left side you will see BROWSER below that there is a option named Servers , click on the Servers it will ask password , enter the password which u typed during setup of postgre and pgadmin4. After this you will see option named PostgreSQl below this there is a option named Databases , right click on Databases and click create, it will ask database name ...just enter any database name and click on save.( Remember: enter only the database name and save)


6. Configure database settings in settings.py which is in the folder named Digital_Voting

        * In settings.py , from 79th line to 85th line  make the changes
        * In the name option enter the name of database which you have given in pgadmin4 and enter the password which you have typed during pgadmin setup .....leave the remaining options which are ENGINE,USER and HOST as it is.

        * For example my database name is harish and my setup password is adithya, you have to make changes given below (remember leave the options ENGINE,USER and HOST as it is)
         
         DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'harish',
        'USER': 'postgres',
        'PASSWORD':'adithya',
        'HOST':'localhost'
    }
}


7. Once Configuration in settings.py is done, run this syntax in terminal SYNTAX: python manage.py migrate

8. Create an account on https://2factor.in and paste api key from your 2factor account in voter/views.py at line 33, 48, 249 and 266 for SMS OTP verification.

For example your API is 3l8eaf1e-ed69-18ed-ahsf-0200cd936042
*then you have to paste API like this in views.py which i have given below

line 33 :  url = "http://2factor.in/API/V1/3l8eaf1e-ed69-18ed-ahsf-0200cd936042/SMS/" + user_phone + "/AUTOGEN"

line 48 : url = "http://2factor.in/API/V1/3l8eaf1e-ed69-18ed-ahsf-0200cd936042/SMS/VERIFY/" + request.session[
            'otp_session_data'] + "/" + userotp

line 249 : url = "http://2factor.in/API/V1/3l8eaf1e-ed69-18ed-ahsf-0200cd936042/SMS/" + vmobno + "/AUTOGEN"

line 266 :  url = "http://2factor.in/API/V1/3l8eaf1e-ed69-18ed-ahsf-0200cd936042/SMS/VERIFY/" + request.session['otp_session_data'] + "/" + userotp


9. Update email_id and password in settings.py in line 137 and 138 for email OTP verification.

10. Run the two syntax given below in terminal 

  First Syntax  1. Syntax : python manage.py createsuperuser

      After this syntax, it will ask username , email and  password.....enter any username , mail and password and remember it(for example username: karthi, email:karthi@gmail.com, password:karthi123)

  Second Sytax  2. Syntax : python manage.py runserver


11. After running the above syntax it will display like this 
     * Starting development server at http://127.0.0.1:8000/  .....press ctrl and left click on this link to display website

     * Once the website is displayed, on the above you will see the url like this http://127.0.0.1:8000/

     * change that url to http://127.0.0.1:8000/admin and click enter
      

12.  The changed url http://127.0.0.1:8000/admin will display Django Administration and it will ask username and password....enter the name and password which u have given during createsuperuser(for eample username:karthi, password:karthi123 )

13. After entering username and password you will see the EC_admin option on left side, click on add...it will display form and you have to fill all and click save ....(remember the Ecadmin id in this form)
*For example my  Ecadmin_id is vinoth

14. after filling the form go to AUTHENTICATION AND AUTHORIZATION option on left side and click users it will ask username , enter the Ecadmin id which u have given during form fill up in username option and enter any password in password option(Remember the Ecadmin_id which is the username and password)..
*Here my username is vinoth beacuse it is my Ecadmin_id  and my password is vinoth123


After entering username and password...click tick to active, staff status and superuser staus in permissions and below the permission you will see USER PERMISSIONS ....below the USER PERMISSION you will see Choose all click that and save


 

15. After finishing above go to this link http://127.0.0.1:8000 and login as admin ...enter the username and password which u have given during the above AUTHENTICATION AND AUTHORIZATION (i.e username:vinoth and password:vinoth123)

16. Now you can able to generate election, add voters and candidates......very very important(Remember during election generation, add candidate and add voter , the state option should be filled only as gujarat the thing is that it will work correct only for gujarat or you can make changes in html pages).

In the add voter, the voterID should be in this form for example SPB2595839 and the voter image to be submitted should be captured in laptop cam...(Remember that all the photos and videos that you are going to upload in voters info should be captured only in laptop cam ..then only it will work)

17. After adding the voter , go to login page you will see the Register option below Forgot Password....click on register , it will ask the voterID and enter the voter id which you have given above during add voter....after entering the VoterId it will send OTP to the mobile number which you have given during add voter...enter the otp and it will display voter info and ask to enter password( enter any password and remember), email and upload video of 5-10 sec(video should capured only in laptop).....after this face detection process occurs and display the message Voter registered

18. After this go to login page and login as voter and enter the VoterID and password(This password is which u have given after otp verification in register option)
 
19. Now the voter can vote for any candidate







