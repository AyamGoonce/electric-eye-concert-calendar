(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.227af94cd148d561.js","sha256":"227af94cd148d561da90f8483f9b1b460f7bca33f90a78e1b99335458a71acc7","count":2161,"publishedAt":"2026-11-11T18:17:02Z","state":"calendar-state.json","stateSha256":"22f40d43f6a8ebf08ab19678457b0897d025aebcdeda60622deb3c8e776fd83e","sourceState":"calendar-source-state.json","sourceStateSha256":"ba341e49555ca87e143a6136eafbad2d862624787b1d66cfdafe780cbd6bec71"});
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
