import colander as c


class RegistrationSchema(c.Schema):

    email = c.SchemaNode(c.String(),
                         validator=c.Email())
