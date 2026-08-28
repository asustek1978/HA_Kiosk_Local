# Security

## Local API

HA Kiosk exposes a local HTTP API, normally on TCP port `2323`.

Authentication is performed with the `X-HA-Kiosk-Key` header.

The current API is **HTTP, not HTTPS**, because it is intended for a trusted local network.

Recommendations:

- do not expose port 2323 to the public Internet;
- use a trusted LAN/VLAN between Home Assistant and the kiosk device;
- keep the API key secret;
- use DHCP reservation or another stable address for the tablet;
- if untrusted clients share the LAN, isolate IoT/kiosk devices with firewall rules while allowing Home Assistant to reach the tablet.

## Camera and microphone

Camera and microphone capture requires Android runtime permissions. Presence monitoring can keep low-resolution camera/microphone processing active in the background depending on configured features.

Disable motion/sound/camera features that are not needed.

## Device Owner

Device Owner is a privileged Android management role. Enable it only on a device intended to be managed as a kiosk/dedicated device. It enables actions such as full device reboot and can affect normal consumer-device behavior.
