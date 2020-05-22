"""
Switch Platform support for pfSense firewall rules.

For more details please refer to
https://github.com/dgshue/home-assistant-custom-components

Example usage:

configuration.yaml

---------------------------------------

switch:
  - platform: pfsense_rule
    host: 192.168.1.1
    api_key: PFFA1QDKsakjied21
    access_token: AectmzLxeTS413I6FtLyA3xhFxs3Y80n3bZEu6gzboxd5adUbbrejFZae1u5
    rule_filter: HomeAssistant


---------------------------------------

"""
import logging
import subprocess

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import (
    SwitchEntity, PLATFORM_SCHEMA, ENTITY_ID_FORMAT)
from homeassistant.const import (
    CONF_FRIENDLY_NAME, CONF_SWITCHES, CONF_VALUE_TEMPLATE, CONF_HOST, CONF_API_KEY, CONF_ACCESS_TOKEN)

CONF_RULE_FILTER = 'rule_filter'

DOMAIN = "switch"

REQUIREMENTS = ['pfsense-fauxapi==20190317.1']


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
    vol.Optional(CONF_RULE_FILTER): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Initialize the platform"""

    """Setup the pfSense Rules platform."""
    import pprint, sys
    from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi

    # Assign configuration variables. The configuration check takes care they are
    # present.
    host = config.get(CONF_HOST)
    api_key = config.get(CONF_API_KEY)
    access_token = config.get(CONF_ACCESS_TOKEN)
    rule_prefix = config.get(CONF_RULE_FILTER)

    _LOGGER.debug("Connecting to pfSense firewall to collect rules to add as switches.")

    try:
        FauxapiLib = PfsenseFauxapi(host, api_key, access_token, debug=True)

        # Get the current set of filters
        filters = FauxapiLib.config_get('filter')

        _LOGGER.debug("Found %s rules in pfSense", len(filters['rule']))

        if rule_prefix:
            _LOGGER.debug("Filter for rules starting with %s being applied", rule_prefix)

        rules = []
        # Iterate through and find rules
        i = 0
        for rule in filters['rule']:
            if rule_prefix:
                if (rule['descr'].startswith(rule_prefix)):
                    _LOGGER.debug("Found rule %s", rule['descr'])
                    new_rule = pfSense('pfsense_'+rule['descr'],rule['descr'],rule['tracker'], host, api_key, access_token)
                    rules.append(new_rule)
            else:
                _LOGGER.debug("Found rule %s", rule['descr'])
                new_rule = pfSense('pfsense_'+rule['descr'],rule['descr'],rule['tracker'], host, api_key, access_token)
                rules.append(new_rule)
            i=i+1


        # Add devices
        add_entities(rules)
    except Exception as e:
        _LOGGER.error("Problem getting rule set from pfSense host: %s.  Likely due to API key or secret. More Info:" + str(e), host)

class pfSense(SwitchEntity):
    """Representation of an pfSense Rule."""

    def __init__(self, name, rule_name, tracker_id, host, api_key, access_token):
        _LOGGER.info("Initialized pfSense Rule SWITCH %s", name)
        """Initialize an pfSense Rule as a switch."""
        self._name = name
        self._rule_name = rule_name
        self._state = None
        self._host = host
        self._api_key = api_key
        self._access_token = access_token
        self._tracker_id = tracker_id

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs):
        self.set_rule_state(True)

    def turn_off(self, **kwargs):
        self.set_rule_state(False)

    def update(self):
        """Check the current state of the rule in pfSense"""
        import pprint, sys
        from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi

        _LOGGER.debug("Getting pfSense current rule state for %s", self._rule_name)
        try:
            # Setup connection with devices/cloud
            FauxapiLib = PfsenseFauxapi(self._host, self._api_key, self._access_token, debug=True)

            # Get the current set of filters
            filters = FauxapiLib.config_get('filter')

            for rule in filters['rule']:
                if (rule['tracker'] == self._tracker_id):
                    _LOGGER.debug("Found rule with tracker %s, updating state.", self._tracker_id)
                    if ('disabled' in rule):
                        self._state = False
                    else:
                        self._state = True
        except:
            _LOGGER.error("Problem retrieving rule set from pfSense host: %s.  Likely due to API key or secret.", self._host)

    def set_rule_state(self, action):
        """Setup the pfSense Rules platform."""
        import pprint, sys
        from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi

        _LOGGER.debug("Connecting to pfSense firewall to change rule states.")
        try:
            # Setup connection with devices/cloud
            FauxapiLib = PfsenseFauxapi(self._host, self._api_key, self._access_token, debug=True)

            # Get the current set of filters
            filters = FauxapiLib.config_get('filter')
        except:
            _LOGGER.error("Problem retrieving rule set from pfSense host: %s.  Likely due to API key or secret.", self._host)

        i = 0
        for rule in filters['rule']:
            if (rule['tracker'] == self._tracker_id):
                _LOGGER.info("Found rule changing state rule: %s", self._rule_name)
                if (action == True):
                    if ('disabled' in rule):
                        del filters['rule'][i]['disabled']
                        _LOGGER.debug("Rule %s enabled in config (this has not been pushed back to firewall yet!)", self._rule_name)
                elif (action == False):
                    filters['rule'][i]['disabled'] = ""
                    _LOGGER.debug("Rule %s disabled in config (this has not been pushed back to firewall yet!)", self._rule_name)
            i=i+1

        try:
            _LOGGER.debug("Sending updated rule set to pfSense firewall")
            # Push the config back to pfSense
            filters = FauxapiLib.config_set(filters, 'filter')

            _LOGGER.debug("Reloading the config on pfSense firewall to accept rule changes")
            # Reload the config
            FauxapiLib.send_event("filter reload")
        except:
            _LOGGER.error("Problem sending & reloading rule set from pfSense host: %s.  Likely due to API key or secret.", self._host)
