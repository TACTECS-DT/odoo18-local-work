from odoo.exceptions import UserError


class SelectionHelper(object):
    list = []
    default = None
    flow_rule = {}

    @classmethod
    def name(cls, key):
        selection_dict = dict(cls.list)
        if key in selection_dict:
            return selection_dict[key]

    @classmethod
    def values(cls):
        return list(dict(cls.list))

    @classmethod
    def get_prev_value(cls, current_value):
        current_index = cls.get_index(current_value)
        if isinstance(current_index, int) and current_index > 0:
            prev_index = current_index - 1
            return cls.list[prev_index][0]

    @classmethod
    def get_next_value(cls, current_value):
        current_index = cls.get_index(current_value)
        if isinstance(current_index, int) and current_index + 1 < len(cls.list):
            next_index = current_index + 1
            return cls.list[next_index][0]

    @classmethod
    def get_index(cls, current_value):
        for i, item in enumerate(cls.list):
            if current_value == item[0]:
                return i

    @classmethod
    def check_state_flow_rule(cls, init_state, state):
        """
        Check if the record flow in correct
        :param str init_state: from state
        :param str state: to state
        :return:
        """
        if not init_state or not cls.flow_rule:
            return
        if init_state in cls.flow_rule:
            allowed_states = cls.flow_rule.get(init_state)
            if not allowed_states:
                return
            if state not in allowed_states:
                allowed_states_str = map(cls.name, allowed_states)
                raise UserError('Incorrect flow! Allowed states are: {}'.format(u', '.join(allowed_states_str)))


class State(SelectionHelper):
    list = [
        ('draft', 'Draft'),
        ('approval', 'Approval'),
        ('running', 'Running'),
        ('to_renew', 'To Renew'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    default = 'draft'

    folded = [
        'expired',
        'closed',
        'cancelled',
    ]

    flow_rule = {
        'draft': ('approval', 'running'),
        'approval': ('draft', 'approval', 'running', 'cancelled'),
        'running': ('expired', 'closed', 'to_renew'),
        'expired': ('to_renew',),
        'closed': ('to_renew',),
        'to_renew': ('draft', 'closed'),
        'cancelled': ('draft',),
    }


class ExpiringState(SelectionHelper):
    list = [
        ('expired', 'Expired'),
        ('closed', 'Closed'),
        ('to_renew', 'To Renew'),
    ]
    default = 'expired'


class KanbanState(SelectionHelper):
    """
    * draft + done = "Incoming" state (will be set as Running once the contract has confirmed)
    * running + blocked = "Pending" state (will be set as Closed once the contract has ended)
    * blocked = Shows a warning on the kanban view
    """
    list = [
        ('normal', 'Normal'),
        ('done', 'Done'),
        ('blocked', 'Blocked')
    ]
    default = 'normal'


class ContractType(SelectionHelper):
    list = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ]


class ApproverState(SelectionHelper):
    list = [
        ('to approve', 'To Approve'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    default = list[0][0]


class Visibility(SelectionHelper):
    list = [
        ('employees', 'All Internal Users'),
        ('followers', 'Invited Internal Users'),
    ]
    default = 'employees'


class UseContract(SelectionHelper):
    list = [
        ('no', 'No'),
        ('optional', 'Optional'),
        ('required', 'Required')
    ]
    default = 'no'
