from dataclasses import dataclass


@dataclass
class Master:
    master_id: int
    name: str


@dataclass
class Service:
    service_id: int
    name: str


@dataclass
class Appoinment:
    id: int
    client_name: str
    master_id: int
    service_id: int
    time: str


masters = [Master(master_id=1, name="Александр")]
services = [Service(service_id=1, name="Стрижка")]
appointments: list[Appoinment] = []


def get_master(master_id: int) -> Master | None:
    return next((master for master in masters if master.master_id == master_id), None)


def get_service(service_id: int) -> Service | None:
    return next((service for service in services if service.service_id == service_id), None)


def create_appointment(
    client_name: str,
    master_id: int,
    service_id: int,
    time: str,
) -> Appoinment | None:
    if not isinstance(client_name, str) or not client_name.strip():
        return None
    if not isinstance(time, str) or not time.strip():
        return None
    if type(master_id) is not int or master_id <= 0:
        return None
    if type(service_id) is not int or service_id <= 0:
        return None

    master = get_master(master_id)
    service = get_service(service_id)
    if master is None or service is None:
        return None

    appointment = Appoinment(
        id=len(appointments) + 1,
        client_name=client_name.strip(),
        master_id=master.master_id,
        service_id=service.service_id,
        time=time.strip(),
    )
    appointments.append(appointment)
    return appointment


if __name__ == "__main__":
    first_appointment = create_appointment("Иванова А.А.", 1, 1, "10:00")
    second_appointment = create_appointment("Петрова А.А.", 1, 1, "11:00")

    print("Список записей:")
    for appointment in appointments:
        print(appointment.client_name, appointment.time)
    appointments.clear()
    no_correct_appointment = create_appointment("", 1, 1, "12:00")
    print(len(appointments))
