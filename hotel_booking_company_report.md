# Hotel Booking Business Insights Report

## Executive Summary
- Total analyzed bookings: 27,742 Confirmed/Cancelled bookings.
- Overall cancellation rate: 21.9% (6,070 Cancelled / 27,742 Confirmed + Cancelled).
- Average net revenue: $29,171.
- Average stay length: 4.00 nights.

## Most Meaningful Trends
1. Lead-time cancellations spike in the 26-30 day gap before check-in: 63.0% cancellation rate and 51.1% of all cancellations. Booking dates in this spike range from Apr 01, 2024 - Apr 29, 2025; check-in dates range from May 01, 2024 - May 29, 2025. Why it matters: this points to a likely cancellation-policy or reminder deadline window.
2. Four-night stays cancel at 62.6%, compared with 4.6% for all other stay lengths combined. Why it matters: stay length is a strong cancellation-risk signal.
3. Travel Agent bookings have the highest cancellation rate at 29.7%, while Web is lowest at 18.6%. Why it matters: cancellation management should vary by sales channel.
4. Star rating is not a major cancellation driver: the highest and lowest star-rating cancellation rates differ by only 1.6 percentage points. Why it matters: focus more on lead time, booking channel, and stay length because those show clearer differences.

## Booking Channel Comparison
| Booking Channel | Booking Count | Share % | Cancellation Rate | Avg Net Revenue | Avg Nights |
| --- | --- | --- | --- | --- | --- |
| Travel Agent | 2814 | 10.1% | 29.7% | $29,149 | 3.98 |
| Mobile App | 10700 | 38.6% | 24.2% | $29,062 | 4.00 |
| Web | 14228 | 51.3% | 18.6% | $29,258 | 4.01 |

Direction: Cancellations from Travel Agent bookings are the highest; Web bookings have the lowest cancellation rate. Avg net revenue is broadly stable across channels.

## Room Type Comparison
| Room Type | Booking Count | Share % | Cancellation Rate | Avg Net Revenue | Avg Nights |
| --- | --- | --- | --- | --- | --- |
| Standard | 15309 | 55.2% | 25.2% | $29,209 | 3.99 |
| Suite | 2758 | 9.9% | 19.4% | $29,279 | 3.98 |
| Deluxe | 9675 | 34.9% | 17.4% | $29,081 | 4.02 |

Direction: Standard rooms have the highest cancellation rate; Deluxe has the lowest. Avg net revenue and nights show no meaningful difference.

## Star Rating Comparison
| Star Rating | Booking Count | Share % | Cancellation Rate | Avg Net Revenue | Avg Nights |
| --- | --- | --- | --- | --- | --- |
| 5 | 4172 | 15.0% | 23.0% | $28,826 | 4.00 |
| 3 | 9712 | 35.0% | 21.8% | $29,305 | 4.01 |
| 4 | 11084 | 40.0% | 21.7% | $29,173 | 3.99 |
| 2 | 2774 | 10.0% | 21.3% | $29,214 | 4.02 |

Direction: Star rating is not a major cancellation driver; the highest and lowest star-rating cancellation rates differ by only 1.6 percentage points.

## Lead-Time Cancellation Analysis
| Lead-Time Band | Bookings | Cancellations | Cancellation Rate | Share of Cancellations |
| --- | --- | --- | --- | --- |
| 1-5 | 1886 | 88 | 4.7% | 1.4% |
| 6-10 | 1928 | 88 | 4.6% | 1.4% |
| 11-15 | 1979 | 99 | 5.0% | 1.6% |
| 16-20 | 1894 | 77 | 4.1% | 1.3% |
| 21-25 | 1845 | 89 | 4.8% | 1.5% |
| 26-30 | 4924 | 3102 | 63.0% | 51.1% |
| 31-35 | 3908 | 2104 | 53.8% | 34.7% |
| 36-40 | 1842 | 78 | 4.2% | 1.3% |
| 41-45 | 1881 | 94 | 5.0% | 1.5% |
| 46-50 | 1836 | 86 | 4.7% | 1.4% |
| 51-55 | 1999 | 83 | 4.2% | 1.4% |
| 56-60 | 1820 | 82 | 4.5% | 1.4% |

Cancellation behavior is concentrated, not evenly spread. The largest spike is 26-30 days before check-in, accounting for 51.1% of all cancellations. Booking dates in this spike range from Apr 01, 2024 - Apr 29, 2025; check-in dates range from May 01, 2024 - May 29, 2025.

## Additional Checks
- City cancellation-rate spread: 1.6 percentage points, so city is not a major driver.
- Stay type cancellation-rate spread: 0.4 percentage points, so Business vs Leisure is not a major driver.
- `channel_of_booking` was ignored because it is a device field, not a sales channel.
- Cancellation was measured only from `booking_status`; refund columns were not used.
