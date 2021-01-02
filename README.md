# Home-Assistant Custom Components

My first iteration of some custom components for home-assistant. (http://www.home-assistant.io)

Component Overview
------------------
  * [pfSense Rule Switch](#pfsense_rule)
  
  
## pfSense Rule Switch Component

This component is written to toggle pfSense firewall rules on (enabled) or off (disabled).  One my question why in the world would someone want to do this from HA. Simply put, I have children that from time to time refuse to clean their rooms and require further motivation on the fly vs on a strict schedule.  However, I'm sure someone else might find a better use case other than messy kids.

### Pre-Reqs

- pfSense 2.3.x or 2.4.x
- FauxAPI 1.3+ installed
  https://github.com/ndejong/pfsense_fauxapi#installation
- FauxAPI API Key and Secret with appropriate permissions

### Installation

- Copy directory `pfsense_rule` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

switch:
  - platform: pfsense_rule
    host: 192.168.1.1
    api_key: PFFA1QDKsakjied21 -or- !secret fauxapi-key
    access_token: AectmzLxeTS413I6FtLyA3xhFxs3Y80n3bZEu6gzboxd5adUbbrejFZae1u5 -or- !secret fauxapi-secret
    rule_filter: HomeAssistant
```

Configuration variables:

- **host** (*Required*): The hostname or IP address of the pfSense firewall, ideally the LAN IP
- **api_key** (*Required*): The API Key from FauxAPI
- **access_token** (*Required*): The API Secret from FauxAPI
- **rule_filter** (*Optional*): Used to create switches only on certain rules.  Rule description must start with filter to match (ie. HomeAssisant-BlockTraffic1)
