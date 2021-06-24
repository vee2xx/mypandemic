from models.user import User


def test_add_user():
    new_user = User()
    new_user.username = 'test1'
    new_user.coutry = 'Canada'
    new_user.region = 'British Columbia'
    new_user.timezone = 'America/Vancouver'
    new_user.phone_number = '1112223333'
    new_user.email = 'test1@slugsy.me'
    new_user.preferences = '{"testsetting": "blah"}'

    new_user.save()

def test_find_user():
    
    new_user.delete()


test_add_user()