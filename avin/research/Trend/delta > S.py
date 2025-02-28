#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Subject # {{{
Меня интересуют все дельты больше маленьких, то есть нормальные, большие и
очень большие: M L XL. Точнее меня интересует вероятность этого события.
    p(delta(0) > S)

А еще точнее меня интересует постапостериорная вероятность этого события
после определенного тренда. Есть ли какой то такой тренд(1) после которого
вероятность что у тренда(0) будет delta > S будет сильно высокой?

Начну рассматривать только дельты.

Posterior
P(H|obs) = P(delta(0) > S | delta(1) = XS)
P(H|obs) = P(delta(0) > S | delta(1) = S)
P(H|obs) = P(delta(0) > S | delta(1) = M)
P(H|obs) = P(delta(0) > S | delta(1) = L)
P(H|obs) = P(delta(0) > S | delta(1) = XL)

Prior
p(H) = p(delta(0) > S)
p(H) = p(delta(0) <= S)

Likehood
p(obs|H) = p(delta(1) = XS | delta(0) > S)
p(obs|H) = p(delta(1) = XS | delta(0) <= S)
p(obs|H) = p(delta(1) = S | delta(0) > S)
p(obs|H) = p(delta(1) = S | delta(0) <= S)
p(obs|H) = p(delta(1) = M | delta(0) > S)
p(obs|H) = p(delta(1) = M | delta(0) <= S)
p(obs|H) = p(delta(1) = L | delta(0) > S)
p(obs|H) = p(delta(1) = L | delta(0) <= S)
p(obs|H) = p(delta(1) = XL | delta(0) > S)
p(obs|H) = p(delta(1) = XL | delta(0) <= S)

"""  # }}}

from __future__ import annotations

from avin import *


class BigDelta:
    @classmethod  # definePrior  # {{{
    def definePrior(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info(f":: Define prior {asset.ticker}-{tf} {term}")

        trend = super().load(
            asset, f"Trend {tf} {term} {TrendAnalytic.Analyse.TREND}"
        )
        trend["delta_ssize"] = trend["delta_ssize"].apply(
            lambda x: SimpleSize.fromStr(x)
        )
        total_count = len(trend)
        prior = pd.DataFrame(columns=["prior", "p"])

        p_xs = len(trend[trend["delta_ssize"] == "XS"]) / total_count
        p_s = len(trend[trend["delta_ssize"] == "S"]) / total_count
        p_m = len(trend[trend["delta_ssize"] == "M"]) / total_count
        p_l = len(trend[trend["delta_ssize"] == "L"]) / total_count
        p_xl = len(trend[trend["delta_ssize"] == "XL"]) / total_count
        prior.loc[len(prior)] = ("delta = XS", p_xs)
        prior.loc[len(prior)] = ("delta = S", p_s)
        prior.loc[len(prior)] = ("delta = M", p_m)
        prior.loc[len(prior)] = ("delta = L", p_l)
        prior.loc[len(prior)] = ("delta = XL", p_xl)

        p_l_xs = len(trend[trend["delta_ssize"] < "XS"]) / total_count
        p_l_s = len(trend[trend["delta_ssize"] < "S"]) / total_count
        p_l_m = len(trend[trend["delta_ssize"] < "M"]) / total_count
        p_l_l = len(trend[trend["delta_ssize"] < "L"]) / total_count
        p_l_xl = len(trend[trend["delta_ssize"] < "XL"]) / total_count
        prior.loc[len(prior)] = ("delta < XS", p_l_xs)
        prior.loc[len(prior)] = ("delta < S", p_l_s)
        prior.loc[len(prior)] = ("delta < M", p_l_m)
        prior.loc[len(prior)] = ("delta < L", p_l_l)
        prior.loc[len(prior)] = ("delta < XL", p_l_xl)

        p_g_xs = len(trend[trend["delta_ssize"] > "XS"]) / total_count
        p_g_s = len(trend[trend["delta_ssize"] > "S"]) / total_count
        p_g_m = len(trend[trend["delta_ssize"] > "M"]) / total_count
        p_g_l = len(trend[trend["delta_ssize"] > "L"]) / total_count
        p_g_xl = len(trend[trend["delta_ssize"] > "XL"]) / total_count
        prior.loc[len(prior)] = ("delta > XS", p_g_xs)
        prior.loc[len(prior)] = ("delta > S", p_g_s)
        prior.loc[len(prior)] = ("delta > M", p_g_m)
        prior.loc[len(prior)] = ("delta > L", p_g_l)
        prior.loc[len(prior)] = ("delta > XL", p_g_xl)

        # save priors
        prior = prior.set_index("prior")
        prior = prior.sort_index()
        name = f"Trend {tf} {term} {TrendAnalytic.Analyse.PRIOR}"
        super().save(asset, name, prior)

    # }}}
    @classmethod  # defineLikehood  # {{{
    def defineLikehood(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info(f":: {cls.name} define prior {asset.ticker}-{tf} {term}")

        trend = super().load(asset, f"Trend {tf} {term} {cls.Analyse.TREND}")
        trend["delta_ssize"] = trend["delta_ssize"].apply(
            lambda x: SimpleSize.fromStr(x)
        )
        total_count = len(trend)
        like = pd.DataFrame(columns=["obs", "H", "p"])

    # }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
