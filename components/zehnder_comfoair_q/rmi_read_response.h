#pragma once

#include <cstdint>
#include <vector>

namespace zehnder_comfoair_q {

enum class RmiReadStatus { IGNORED, INCOMPLETE, COMPLETE, INVALID };

class RmiReadResponse {
public:
    void start(uint8_t sequence, uint8_t local_node, uint8_t remote_node) {
        sequence_ = sequence;
        local_node_ = local_node;
        remote_node_ = remote_node;
        next_fragment_ = 0;
        error_ = false;
        data_.clear();
        active_ = true;
    }
    void cancel() { active_ = false; data_.clear(); }
    bool active() const { return active_; }
    bool error() const { return error_; }
    const std::vector<uint8_t> &data() const { return data_; }

    RmiReadStatus receive(uint32_t id, bool extended, bool rtr, const std::vector<uint8_t> &payload) {
        if (!active_ || !extended || rtr || (id & 0x1ff90000) != 0x1f000000 ||
            (id & 0x3f) != remote_node_ || ((id >> 6) & 0x3f) != local_node_ ||
            ((id >> 17) & 3) != sequence_)
            return RmiReadStatus::IGNORED;
        const bool fragmented = id & (1u << 14);
        const bool error = id & (1u << 15);
        if (payload.size() > 8 || (fragmented && payload.empty()) ||
            (next_fragment_ && (!fragmented || error != error_)))
            return invalid_();
        error_ = error;
        if (!fragmented) {
            data_ = payload;
            active_ = false;
            return RmiReadStatus::COMPLETE;
        }
        if ((payload[0] & 0x7f) != next_fragment_ || data_.size() + payload.size() - 1 > 256)
            return invalid_();
        data_.insert(data_.end(), payload.begin() + 1, payload.end());
        next_fragment_++;
        if (payload[0] & 0x80) {
            active_ = false;
            return RmiReadStatus::COMPLETE;
        }
        return RmiReadStatus::INCOMPLETE;
    }

private:
    RmiReadStatus invalid_() { cancel(); return RmiReadStatus::INVALID; }
    bool active_ = false;
    bool error_ = false;
    uint8_t sequence_ = 0, local_node_ = 0, remote_node_ = 0, next_fragment_ = 0;
    std::vector<uint8_t> data_;
};

} // namespace zehnder_comfoair_q
