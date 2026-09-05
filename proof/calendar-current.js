(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2073ac81b1908811.js","sha256":"2073ac81b1908811848ed3358c60eb027955b389031859ab9ce2e21f89db6fe4","count":2525,"publishedAt":"2026-09-05T09:04:31Z","state":"calendar-state.json","stateSha256":"27204811c456f6c8f673656b42532077090f05d8aba4bf272b82feba19494316"});
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
