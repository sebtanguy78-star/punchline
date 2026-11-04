// Vidéo 2 — cartes (panneau à gauche). Helpers globaux du template : $, pr, clamp, eOut, eIn, eIO, eBack, vis, slide, pop, slam.
window.renderCards = function (t) {
  let e;
  e = E.name;
  slide($('name'), t, e.t_in, e.t_out);
  { const x = eOut(pr(t, e.t_name, .45)); const nm = $('name').querySelector('.nm span');
    nm.style.transform = `translateY(${(1 - x) * 105}%)`; nm.style.opacity = x > 0 ? 1 : 0;
    $('name').querySelector('.ul').style.transform = `scaleX(${eIO(pr(t, e.t_name + .12, .5))})`; }
  e = E.loc;
  slide($('loc'), t, e.t_in, e.t_out);
  $('loc').querySelector('.sub').style.opacity = eOut(pr(t, e.t_sub, .3));
  pop($('locchip'), t, e.t_chip, e.t_out);

  e = E.studio;
  slide($('studio'), t, e.t_in, e.t_out);
  pop($('st1'), t, e.t_c1, e.t_out); pop($('st2'), t, e.t_c2, e.t_out);

  e = E.formats;
  slide($('formats'), t, e.t_in, e.t_out);
  pop($('fm1'), t, e.t_c1, e.t_out); pop($('fm2'), t, e.t_c2, e.t_out); pop($('fm3'), t, e.t_c3, e.t_out);

  e = E.projets;
  slide($('projets'), t, e.t_in, e.t_out);
  pop($('pj1'), t, e.t_c1, e.t_out); pop($('pj2'), t, e.t_c2, e.t_out);
  pop($('pj3'), t, e.t_c3, e.t_out); pop($('pj4'), t, e.t_c4, e.t_out);

  e = E.decors;
  slide($('decors'), t, e.t_in, e.t_out);
  [['dc1', e.t_c1], ['dc2', e.t_c2]].forEach(([id, t0]) => {
    const r = $(id), x = pr(t, t0, .3);
    r.style.opacity = clamp(x * 2.5); r.style.transform = `translateX(${(1 - eOut(x)) * 30 * DIR}px)`;
    r.querySelector('.ck').style.transform = `scale(${.3 + .7 * eBack(x)})`;
    r.querySelector('path').style.strokeDashoffset = 30 * (1 - eOut(pr(t, t0 + .1, .3)));
  });

  e = E.matoile;
  slide($('mt'), t, e.t_in, e.t_out);
  { const x = pr(t, e.t_in + .08, .45);
    $('mt').querySelector('.logo').style.transform = `scale(${.3 + .7 * eBack(x, 2.2)}) rotate(${(1 - eOut(x)) * -12}deg)`;
    $('mt').querySelector('.stripes').style.transform = `skewX(-35deg) scaleX(${eIO(pr(t, e.t_in + .3, .45))})`; }
  pop($('mt1'), t, e.t_c1, e.t_out);

  e = E.yt;
  slide($('yt'), t, e.t_in, e.t_out);

  e = E.trio;
  slide($('triotag'), t, e.t_in, e.t_out);
  slam($('tw1'), t, e.t_w1, e.t_out, -3); slam($('tw2'), t, e.t_w2, e.t_out, 2); slam($('tw3'), t, e.t_w3, e.t_out, -2);
  pop($('triochip'), t, e.t_chip, e.t_out);

  e = E.partant;
  slide($('partant'), t, e.t_in, e.t_out);
  pop($('pa1'), t, e.t_c1, e.t_out); pop($('pa2'), t, e.t_c2, e.t_out);
};
window.cardsReady = () => { $('st2').style.left = ($('st1').offsetWidth + 18) + 'px'; };
