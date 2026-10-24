(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.eb4cbd4d638b8f4a.js","sha256":"eb4cbd4d638b8f4a49ee7f13ff5384729348c636a5b099ea1e8c15d03206f580","count":2078,"publishedAt":"2026-10-24T16:04:24Z","state":"calendar-state.json","stateSha256":"12b3a41a3a49de6a3072a47fe49f04cddab942bcae62062e3c687f15796bd2fb","sourceState":"calendar-source-state.json","sourceStateSha256":"0c94320bddced719289c0071f053f0d4685df1c464c467d324918d7bc05d1c61"});
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
