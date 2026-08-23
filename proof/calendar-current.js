(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.930ecdd83f6e68c3.js","sha256":"930ecdd83f6e68c3862c18c9fdeb40fc0fe43b37a73b7a834558e42e197ef1bc","count":1732});
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
