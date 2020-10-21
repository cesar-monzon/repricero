import re


def price_outlier_check(prices, pct_diff = 10):
    """ Returns lowest valid price that is within pct_diff range to higher neighbor
        Args:
            prices: list of lowest prices
            pct_diff: allowable percentage difference from high price to lower neighbor
        Returns:
            lowest valid price
    """
    valid_price = prices[-1]
    
    for price in reversed(prices[:-1]):
        if (valid_price - (valid_price * (pct_diff / 100))) >= price:
            break
        valid_price = price

    return valid_price


def filter_competitors(response, **pref):
    """ Returns lowest valid price that is within pct_diff range to higher neighbor
        Args:
            response: mws get item pricing api response
            pref: user preferences on competition to ignore
        Returns:
            list of valid competitors price and condition
    """
    competitors = []
    
    subcondition = {'New': 1,
                    'Mint': 2, 'LikeNew' : 2, 'NotUsed': 2,
                    'VeryGood': 3,
                    'Good': 4, 'Club': 4, 'OEM': 4, 'Warranty': 4,
                    'Refurbished': 4, 'OpenBox': 4, 'Other': 4,
                    'Acceptable': 5,
                    'Poor': 6, 'Unacceptable':6
                    }

    offers = response.Product.LowestOfferListings.LowestOfferListing

    for offer in offers:

        feedback_pct = re.findall('-(\d+)?\%', offer.Qualifiers.SellerPositiveFeedbackRating)
        feedback_pct = int(feedback_pct[0]) if feedback_pct else 0 
        
        if ignore_new_sellers and not feedback_pct: continue
        
        if (int(offer.SellerFeedbackCount) < min_feedback
            or feedback_pct < min_feedback_pct): continue

        seller_offers = int(offer.MultipleOffersAtLowestPrice == 'True')
        
        for listing in range(seller_offers + 1):
            competitors.append((float(offer.Price.LandedPrice.Amount), subcondition[offer.Qualifiers.ItemSubcondition]))

    if len(competitors) < comp_needed: competitors = []

    return competitors

