import colander as c
import deform.widget as w


class RegistrationSchema(c.Schema):

    email = c.SchemaNode(c.String(),
                         validator=c.Email())


class ActivationSchema(c.Schema):

    username = c.SchemaNode(c.String())
    password = c.SchemaNode(c.String(),
                            widget=w.PasswordWidget())


class UserProfileSchema(c.Schema):

    given_name = c.SchemaNode(c.String())
    family_name = c.SchemaNode(c.String())
    nick = c.SchemaNode(c.String())
    gender = c.SchemaNode(c.String(),
                          validator=c.OneOf(['male',
                                             'female']))
    plan = c.SchemaNode(c.String())


class LoginSchema(c.Schema):

    username = c.Schema(c.String())
    password = c.Schema(c.String(),
                        widget=w.PasswordWidget())
