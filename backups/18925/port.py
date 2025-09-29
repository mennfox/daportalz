import board
import busio
import smbus2

def scan_busio():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        addresses = i2c.scan()
        i2c.unlock()
        return set(addresses)
    except Exception as e:
        print(f"busio scan error: {e}")
        return set()

def scan_smbus2():
    found = set()
    try:
        bus = smbus2.SMBus(1)
        for address in range(0x03, 0x77):
            try:
                bus.read_byte(address)
                found.add(address)
            except:
                continue
    except Exception as e:
        print(f"smbus2 scan error: {e}")
    return found

def deep_i2c_scan():
    busio_addrs = scan_busio()
    smbus_addrs = scan_smbus2()
    all_addrs = sorted(busio_addrs.union(smbus_addrs))

    print("\n🔍 I²C Address Scan Results")
    for addr in all_addrs:
        tags = []
        if addr in busio_addrs:
            tags.append("busio")
        if addr in smbus_addrs:
            tags.append("smbus2")
        print(f" - {hex(addr)} [{', '.join(tags)}]")

if __name__ == "__main__":
    deep_i2c_scan()

