#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/containers/map.hpp>
#include <boost/interprocess/sync/named_upgradable_mutex.hpp>
#include <boost/interprocess/sync/sharable_lock.hpp>
#include <array>
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/tuple.hpp>
#include <boost/rational.hpp>
#include <boost/config.hpp>
#include <utility>
#include <vector>

#define SIDEBOOK_SIZE       100
#define ZEROVAL             number(0, 1)
#define MAXVAL              number(2147483645, 1)
#define EXCHANGECOUNT         10

using namespace boost::interprocess;
using boost::rational;

enum shm_mode { read_shm, read_write_shm };

typedef long long base_number;
typedef managed_shared_memory::segment_manager 									 	segment_manager_t;
typedef allocator<void, segment_manager_t>                           				void_allocator;

typedef rational<base_number>                                                       number;

typedef std::array<number, 2>                                                       orderbook_entry_type;
typedef std::array<number, 4>                                                       orderbook_row_type;

typedef orderbook_entry_type::iterator                                              entry_ascender;
typedef orderbook_entry_type::reverse_iterator                                      entry_descender;

typedef uint                                                                        exchange_type;

typedef std::pair<number, number>                                                   orderbook_entry_rep;
typedef std::vector<orderbook_entry_rep >                                           orderbook_extract;

typedef std::array< orderbook_row_type, SIDEBOOK_SIZE>                              sidebook_content;
typedef sidebook_content::iterator                                                  sidebook_ascender;
typedef sidebook_content::reverse_iterator                                          sidebook_descender;


number quantity(sidebook_content::iterator loc);

number price(sidebook_content::iterator loc);

number quantity(sidebook_content::reverse_iterator loc);

number price(sidebook_content::reverse_iterator loc);


class SideBook {
    mapped_region *region;
    managed_shared_memory *segment;
    sidebook_content *data;
    void_allocator *allocator;
    number default_value;
    shm_mode book_mode;

    void fill_with(number);
    number get_row_total(orderbook_row_type*);

    void setup_segment (std::string, shm_mode);
    void insert_at_place(sidebook_content*, orderbook_entry_type, exchange_type, sidebook_content::iterator);

	public:
        SideBook(std::string, shm_mode, number);


        named_upgradable_mutex *mutex;
        number** snapshot_to_limit(int);
        boost::python::list py_snapshot_to_limit(int);

        void insert_ask(number, number, exchange_type);
        void insert_bid(number, number, exchange_type);
        void reset_content();

        number get_default_value() {
          return default_value;
        }

        sidebook_ascender begin();
        sidebook_ascender end();
};
