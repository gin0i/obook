#include <boost/python.hpp>
#include "orderbook.hpp"

using namespace boost::python;

BOOST_PYTHON_MODULE(orderbook_wrapper)
{
    class_< SideBook >("SideBook", init<std::string, shm_mode, number>());

    class_< OrderbookReader >("OrderbookReader")
        .def("init_shm", &OrderbookReader::init_shm)
        .def("bids_up_to_volume", &OrderbookReader::py_bids_up_to_volume)
        .def("asks_up_to_volume", &OrderbookReader::py_asks_up_to_volume)
        .def("snapshot_bids", &OrderbookReader::py_snapshot_bids)
        .def("snapshot_asks", &OrderbookReader::py_snapshot_asks)
        .def("first_price", &OrderbookReader::first_price);

    class_< OrderbookWriter >("OrderbookWriter")
        .def("init_shm", &OrderbookWriter::init_shm)
        .def("bids_up_to_volume", &OrderbookReader::py_bids_up_to_volume)
        .def("asks_up_to_volume", &OrderbookReader::py_asks_up_to_volume)
        .def("snapshot_bids", &OrderbookReader::py_snapshot_bids)
        .def("snapshot_asks", &OrderbookReader::py_snapshot_asks)
        .def("first_price", &OrderbookReader::first_price)
        .def("set_quantity_at", &OrderbookWriter::set_quantity_at);
}
