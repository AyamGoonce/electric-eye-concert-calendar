(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.12e68b67c6b435ef.js","sha256":"12e68b67c6b435ef28628d2e0234d7c4e336bbfd58aeb7dce12d80d501fae28d","count":2062,"publishedAt":"2026-10-21T04:59:40Z","state":"calendar-state.json","stateSha256":"2dc905ccdab2ddf3eebee2b22edf93049e3826bc8523c66102fdada1471f7144","sourceState":"calendar-source-state.json","sourceStateSha256":"dbc86a22994e8016732ad709b7235e7dee4d8aab0587f634f58ffa988f9441b0"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
