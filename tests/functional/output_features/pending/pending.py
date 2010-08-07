# -*- coding: utf-8 -*-
from lettuce import step
from lettuce.utils import pending

@step(u'I have a pending step')
def i_have_a_pending_step(step):
    pending()

@step(u'this failing step will never run')
def this_failing_step_will_never_run(step):
    assert False

@step(u'Given I have a passing step')
def given_i_have_a_passing_step(step):
    pass


