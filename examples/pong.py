from gevent import monkey  # isort:skip
monkey.patch_all()  # isort:skip

from time import sleep  # noqa: E402

from ge_amqp import AmqpParameters  # noqa: E402
from ge_amqp_rpc import AmqpRpc, Service  # noqa: E402

rpc_conn = AmqpRpc(
    AmqpParameters(),
    'pong',
)

PingClient = rpc_conn.client('ping', 'ping')


class PongService:
    svc = Service('pong')

    @svc.rpc
    def pong(name: str):
        resp = PingClient.ping(name)
        return 'resp [{}]: {}'.format(
            resp.status,
            resp.body,
        )


pong_service = PongService()

rpc_conn \
    .add_svc(pong_service)

rpc_conn.configure()
rpc_conn.start(wait=False)

while True:
    sleep(1)
    print(pong_service.pong('duck'))
