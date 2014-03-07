import colander as c
import deform.widget as w


class RegistrationSchema(c.Schema):

    email = c.SchemaNode(c.String(),
                         validator=c.Email())


class ActivationSchema(c.Schema):

    username = c.SchemaNode(c.String())
    password = c.SchemaNode(c.String(),
                            widget=w.PasswordWidget())
